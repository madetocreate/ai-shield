"""
AI-Shield Policy Engine - Zentrale Entscheidungslogik

Pipeline: normalize -> classify -> policy -> redact -> route -> log/metrics
Compatibility Modes: observe, warn, block
"""

import os
import time
import uuid
import logging
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import yaml
except Exception:
    yaml = None

logger = logging.getLogger("policy_engine")
logger.setLevel(logging.INFO)

# Metrics (simple in-memory, in production use Prometheus/StatsD)
_metrics = {
    "decision_count": {},  # decision -> count
    "reason_code_count": {},  # reason_code -> count
    "decision_time_ms": [],  # latency samples
}


class Decision(Enum):
    """Policy Decision Types"""
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"


class CompatibilityMode(Enum):
    """Compatibility Mode: observe (never block), warn (non-breaking), block (hard rejection)"""
    OBSERVE = "observe"
    WARN = "warn"
    BLOCK = "block"


@dataclass
class PolicyRequest:
    """Normalized request for policy evaluation"""
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    preset: Optional[str] = None
    compatibility_mode: Optional[CompatibilityMode] = None


@dataclass
class PolicyDecision:
    """Policy decision result"""
    decision: Decision
    reason_codes: List[str]
    sanitized_request: Optional[Dict[str, Any]] = None
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    rule_triggers: List[Dict[str, Any]] = field(default_factory=list)
    decision_time_ms: float = 0.0


class PolicyEngine:
    """Zentrale Policy Engine für AI-Shield"""
    
    def __init__(self, policies_path: Optional[str] = None, packs_path: Optional[str] = None):
        self.policies_path = policies_path or os.environ.get(
            "AI_SHIELD_POLICY_PATH", "/app/policies/presets.yaml"
        )
        self.packs_path = packs_path or os.environ.get(
            "AI_SHIELD_PACKS_PATH", "/app/policies/packs"
        )
        self._policies_cache: Optional[Dict[str, Any]] = None
        self._packs_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 60
        self._cache_mtime: float = 0
        self._cache_loaded_at: float = 0
    
    def _load_policies(self) -> Dict[str, Any]:
        """Lade Policies mit Caching"""
        p = Path(self.policies_path)
        if not p.exists():
            return {}
        
        try:
            current_mtime = p.stat().st_mtime
            now = time.time()
            
            if (self._policies_cache is not None and
                current_mtime == self._cache_mtime and
                (now - self._cache_loaded_at) < self._cache_ttl):
                return self._policies_cache
            
            if yaml is None:
                return {}
            
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            self._policies_cache = data
            self._cache_mtime = current_mtime
            self._cache_loaded_at = now
            return data
        except Exception as e:
            logger.error(f"Fehler beim Laden von Policies: {e}", extra={"path": self.policies_path})
            return {}
    
    def _load_pack(self, pack_name: str) -> Optional[Dict[str, Any]]:
        """Lade ein Policy Pack"""
        if pack_name in self._packs_cache:
            return self._packs_cache[pack_name]
        
        pack_dir = Path(self.packs_path) / pack_name
        if not pack_dir.exists():
            return None
        
        pack_file = pack_dir / "policy.yaml"
        if not pack_file.exists():
            return None
        
        try:
            if yaml is None:
                return None
            
            data = yaml.safe_load(pack_file.read_text(encoding="utf-8")) or {}
            self._packs_cache[pack_name] = data
            return data
        except Exception as e:
            logger.error(f"Fehler beim Laden von Pack {pack_name}: {e}")
            return None
    
    def _normalize_request(self, raw_request: Dict[str, Any]) -> PolicyRequest:
        """Normalize request: extract messages, tools, metadata"""
        messages = raw_request.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        
        tools = raw_request.get("tools")
        if not isinstance(tools, list):
            tools = None
        
        metadata = raw_request.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        # Extract tenant_id and preset from metadata
        tenant_id = metadata.get("tenant_id") or metadata.get("ai_shield_tenant_id")
        preset = metadata.get("ai_shield_preset") or metadata.get("preset")
        
        # Generate correlation_id if not present
        correlation_id = metadata.get("correlation_id") or metadata.get("ai_shield_request_id")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            metadata["correlation_id"] = correlation_id
            metadata["ai_shield_request_id"] = correlation_id
        
        # Get compatibility mode from metadata or ENV
        compat_mode_str = metadata.get("compatibility_mode") or os.environ.get(
            "AI_SHIELD_COMPATIBILITY_MODE", "block"
        ).lower()
        try:
            compat_mode = CompatibilityMode(compat_mode_str)
        except ValueError:
            compat_mode = CompatibilityMode.BLOCK
        
        return PolicyRequest(
            messages=messages,
            tools=tools,
            metadata=metadata,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            preset=preset,
            compatibility_mode=compat_mode,
        )
    
    def _classify_request(self, request: PolicyRequest) -> Dict[str, Any]:
        """Classify request: extract text, detect PII, injection signals, etc."""
        # Extract text from messages
        text_parts = []
        for msg in request.messages:
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                text_parts.append(msg["content"])
        joined_text = "\n".join(text_parts)
        
        # Load policies to get preset config
        policies = self._load_policies()
        default_preset = policies.get("default_preset", "public_website")
        preset = request.preset or default_preset
        preset_cfg = (policies.get("presets") or {}).get(preset, {})
        
        # Classification results
        classification = {
            "text": joined_text,
            "text_length": len(joined_text),
            "preset": preset,
            "preset_config": preset_cfg,
            "has_tools": bool(request.tools),
            "tool_count": len(request.tools) if request.tools else 0,
        }
        
        return classification
    
    def _evaluate_policy(self, request: PolicyRequest, classification: Dict[str, Any]) -> Tuple[Decision, List[str], List[Dict[str, Any]]]:
        """Evaluate policy rules and return decision, reason_codes, rule_triggers"""
        decision = Decision.ALLOW
        reason_codes: List[str] = []
        rule_triggers: List[Dict[str, Any]] = []
        
        preset_cfg = classification.get("preset_config", {})
        pii_cfg = preset_cfg.get("pii", {})
        text = classification.get("text", "")
        
        # Import detection functions from custom_callbacks
        # Use try/except to handle import errors gracefully
        try:
            from custom_callbacks import (
                _score_injection,
                _find_credit_cards,
                EMAIL_RE,
                PHONE_RE,
            )
        except ImportError:
            # Fallback if custom_callbacks not available
            logger.warning("custom_callbacks not available, using fallback detection")
            import re
            EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
            PHONE_RE = re.compile(r"(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d[\d\s.-]{6,}\d")
            
            def _score_injection(text: str) -> int:
                # Simple fallback
                return 0
            
            def _find_credit_cards(text: str) -> List[str]:
                # Simple fallback
                return []
        
        # Rule 1: Prompt Injection Detection
        injection_threshold = preset_cfg.get("injection_block_threshold", 6)
        injection_score = _score_injection(text)
        if injection_score >= injection_threshold:
            decision = Decision.BLOCK
            reason_codes.append("prompt_injection_detected")
            rule_triggers.append({
                "rule_id": "injection_detection",
                "score": injection_score,
                "threshold": injection_threshold,
            })
        
        # Rule 2: Credit Card Detection
        cc_mode = str(pii_cfg.get("credit_card", "block")).lower()
        if cc_mode == "block":
            credit_cards = _find_credit_cards(text)
            if credit_cards:
                decision = Decision.BLOCK
                reason_codes.append("credit_card_detected")
                rule_triggers.append({
                    "rule_id": "credit_card_block",
                    "count": len(credit_cards),
                })
        
        # Rule 3: PII Detection (email, phone) - only warn/block if configured
        email_mode = str(pii_cfg.get("email", "mask")).lower()
        phone_mode = str(pii_cfg.get("phone", "mask")).lower()
        
        if email_mode == "block" and EMAIL_RE.search(text):
            decision = Decision.BLOCK
            reason_codes.append("email_detected")
            rule_triggers.append({"rule_id": "email_block"})
        elif email_mode == "warn" and EMAIL_RE.search(text):
            if decision == Decision.ALLOW:
                decision = Decision.WARN
            reason_codes.append("email_detected")
            rule_triggers.append({"rule_id": "email_warn"})
        
        if phone_mode == "block" and PHONE_RE.search(text):
            decision = Decision.BLOCK
            reason_codes.append("phone_detected")
            rule_triggers.append({"rule_id": "phone_block"})
        elif phone_mode == "warn" and PHONE_RE.search(text):
            if decision == Decision.ALLOW:
                decision = Decision.WARN
            reason_codes.append("phone_detected")
            rule_triggers.append({"rule_id": "phone_warn"})
        
        # Rule 4: Tool Permission Checks (if tools present)
        if request.tools:
            mcp_cfg = preset_cfg.get("mcp", {})
            risky_regex = mcp_cfg.get("risky_tool_name_regex")
            if risky_regex:
                import re
                risky_re = re.compile(str(risky_regex))
                for tool in request.tools:
                    if not isinstance(tool, dict):
                        continue
                    tool_name = tool.get("function", {}).get("name") or tool.get("name") or ""
                    if risky_re.search(tool_name):
                        decision = Decision.BLOCK
                        reason_codes.append("risky_tool_detected")
                        rule_triggers.append({
                            "rule_id": "risky_tool_block",
                            "tool_name": tool_name,
                        })
                        break
        
        return decision, reason_codes, rule_triggers
    
    def _redact_request(self, request: PolicyRequest, classification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Redact/sanitize request based on policy"""
        preset_cfg = classification.get("preset_config", {})
        pii_cfg = preset_cfg.get("pii", {})
        
        email_mode = str(pii_cfg.get("email", "mask")).lower()
        phone_mode = str(pii_cfg.get("phone", "mask")).lower()
        cc_mode = str(pii_cfg.get("credit_card", "block")).lower()
        
        # Only redact if masking is enabled
        if email_mode != "mask" and phone_mode != "mask" and cc_mode != "mask":
            return None
        
        # Import masking functions from custom_callbacks
        try:
            from custom_callbacks import _mask_text, _find_credit_cards, EMAIL_RE, PHONE_RE
        except ImportError:
            # Fallback if custom_callbacks not available
            logger.warning("custom_callbacks not available, skipping redaction")
            return None
        
        sanitized_messages = []
        for msg in request.messages:
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    sanitized_content = _mask_text(content, email_mode, phone_mode, cc_mode)
                    if sanitized_content != content:
                        sanitized_msg = msg.copy()
                        sanitized_msg["content"] = sanitized_content
                        sanitized_messages.append(sanitized_msg)
                    else:
                        sanitized_messages.append(msg)
                else:
                    sanitized_messages.append(msg)
            else:
                sanitized_messages.append(msg)
        
        if not sanitized_messages:
            return None
        
        return {
            "messages": sanitized_messages,
            "tools": request.tools,
            "metadata": request.metadata,
        }
    
    def _apply_compatibility_mode(
        self, decision: Decision, mode: Optional[CompatibilityMode]
    ) -> Decision:
        """Apply compatibility mode: observe/warn/block"""
        if mode is None:
            mode = CompatibilityMode.BLOCK
        
        if mode == CompatibilityMode.OBSERVE:
            # Never block in observe mode
            return Decision.ALLOW if decision == Decision.BLOCK else decision
        elif mode == CompatibilityMode.WARN:
            # Convert block to warn
            return Decision.WARN if decision == Decision.BLOCK else decision
        else:  # BLOCK
            return decision
    
    def decide(self, raw_request: Dict[str, Any]) -> PolicyDecision:
        """
        Zentrale Entscheidungsmethode
        
        Pipeline: normalize -> classify -> policy -> redact -> route -> log/metrics
        """
        start_time = time.time()
        
        try:
            # 1. Normalize
            request = self._normalize_request(raw_request)
            
            # 2. Classify
            classification = self._classify_request(request)
            
            # 3. Policy Evaluation
            decision, reason_codes, rule_triggers = self._evaluate_policy(request, classification)
            
            # 4. Apply Compatibility Mode
            final_decision = self._apply_compatibility_mode(
                decision, request.compatibility_mode
            )
            
            # 5. Redact (if needed)
            sanitized_request = self._redact_request(request, classification)
            
            decision_time_ms = (time.time() - start_time) * 1000
            
            result = PolicyDecision(
                decision=final_decision,
                reason_codes=reason_codes,
                sanitized_request=sanitized_request,
                tenant_id=request.tenant_id,
                correlation_id=request.correlation_id,
                rule_triggers=rule_triggers,
                decision_time_ms=decision_time_ms,
            )
            
            # 6. Log & Metrics
            self._log_decision(result)
            self._record_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler in Policy Engine: {e}", exc_info=True)
            # Fail-closed: block on error
            decision_time_ms = (time.time() - start_time) * 1000
            return PolicyDecision(
                decision=Decision.BLOCK,
                reason_codes=["policy_engine_error"],
                tenant_id=None,
                correlation_id=str(uuid.uuid4()),
                decision_time_ms=decision_time_ms,
            )
    
    def _log_decision(self, decision: PolicyDecision):
        """Strukturiertes Logging der Entscheidung"""
        log_data = {
            "event": "policy_decision",
            "correlation_id": decision.correlation_id,
            "tenant_id": decision.tenant_id,
            "decision": decision.decision.value,
            "reason_codes": decision.reason_codes,
            "rule_triggers": decision.rule_triggers,
            "decision_time_ms": decision.decision_time_ms,
        }
        
        if decision.decision == Decision.BLOCK:
            logger.warning("Policy decision: BLOCK", extra=log_data)
        elif decision.decision == Decision.WARN:
            logger.info("Policy decision: WARN", extra=log_data)
        else:
            logger.debug("Policy decision: ALLOW", extra=log_data)
    
    def _record_metrics(self, decision: PolicyDecision):
        """Record metrics for observability"""
        # Decision counter
        decision_key = decision.decision.value
        _metrics["decision_count"][decision_key] = _metrics["decision_count"].get(decision_key, 0) + 1
        
        # Reason code counters
        for reason_code in decision.reason_codes:
            _metrics["reason_code_count"][reason_code] = _metrics["reason_code_count"].get(reason_code, 0) + 1
        
        # Decision latency histogram
        _metrics["decision_time_ms"].append(decision.decision_time_ms)
        # Keep only last 1000 samples
        if len(_metrics["decision_time_ms"]) > 1000:
            _metrics["decision_time_ms"] = _metrics["decision_time_ms"][-1000:]
    
    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        """Get current metrics snapshot"""
        latency_samples = _metrics["decision_time_ms"]
        latency_stats = {}
        if latency_samples:
            latency_stats = {
                "count": len(latency_samples),
                "min": min(latency_samples),
                "max": max(latency_samples),
                "avg": sum(latency_samples) / len(latency_samples),
                "p50": sorted(latency_samples)[len(latency_samples) // 2],
                "p95": sorted(latency_samples)[int(len(latency_samples) * 0.95)],
                "p99": sorted(latency_samples)[int(len(latency_samples) * 0.99)],
            }
        
        return {
            "decision_count": dict(_metrics["decision_count"]),
            "reason_code_count": dict(_metrics["reason_code_count"]),
            "decision_time_ms": latency_stats,
        }


# Global instance
_engine_instance: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get or create global policy engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PolicyEngine()
    return _engine_instance

