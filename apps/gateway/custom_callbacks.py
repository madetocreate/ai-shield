import os
import re
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, AsyncGenerator

try:
    import yaml
except Exception:
    yaml = None

from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache

try:
    from litellm.types.utils import ModelResponseStream
except Exception:
    ModelResponseStream = Any

# Logging Setup
logger = logging.getLogger("ai_shield_callback")
logger.setLevel(logging.INFO)

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d[\d\s.-]{6,}\d")
CC_CANDIDATE_RE = re.compile(r"(?:\b(?:\d[ -]*?){13,19}\b)")

INJECTION_SIGNALS = [
    r"ignore (all|any|previous) (instructions|system|developer)",
    r"disregard (all|any|previous) (instructions|system|developer)",
    r"reveal (the )?(system|developer) (prompt|message)",
    r"print (the )?(system|developer) prompt",
    r"show me (the )?(system|developer) (prompt|message)",
    r"jailbreak",
    r"do anything now",
    r"developer mode",
]

# In-Memory Cache für Policies und Registry (mit TTL und mtime-Check)
_CACHE_TTL = 60  # 60 Sekunden TTL
_cache_policies: Optional[Dict[str, Any]] = None
_cache_policies_mtime: float = 0
_cache_policies_loaded_at: float = 0

_cache_registry: Optional[Dict[str, Any]] = None
_cache_registry_mtime: float = 0
_cache_registry_loaded_at: float = 0

def _epoch() -> int:
    return int(time.time())

def _luhn_ok(number: str) -> bool:
    digits = [int(c) for c in number if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    s = 0
    parity = (len(digits) - 2) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d2 = d * 2
            s += d2 - 9 if d2 > 9 else d2
        else:
            s += d
    return s % 10 == 0

def _find_credit_cards(text: str) -> List[str]:
    out: List[str] = []
    for m in CC_CANDIDATE_RE.finditer(text or ""):
        raw = m.group(0)
        digits = "".join([c for c in raw if c.isdigit()])
        if _luhn_ok(digits):
            out.append(raw)
    return out

def _load_yaml(path: str) -> Dict[str, Any]:
    """Lädt YAML mit Caching (reload wenn Datei geändert)"""
    global _cache_policies, _cache_policies_mtime, _cache_policies_loaded_at
    
    p = Path(path)
    if not p.exists():
        return {}
    
    # Prüfe mtime und TTL
    try:
        current_mtime = p.stat().st_mtime
        now = time.time()
        
        if (_cache_policies is not None and 
            current_mtime == _cache_policies_mtime and 
            (now - _cache_policies_loaded_at) < _CACHE_TTL):
            return _cache_policies
        
        # Reload
        if yaml is None:
            return {}
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        _cache_policies = data
        _cache_policies_mtime = current_mtime
        _cache_policies_loaded_at = now
        return data
    except Exception as e:
        logger.error(f"Fehler beim Laden von Policies: {e}", extra={"path": path})
        return {}

def _load_registry(path: str) -> Dict[str, Any]:
    """Lädt Registry JSON mit Caching (reload wenn Datei geändert)"""
    global _cache_registry, _cache_registry_mtime, _cache_registry_loaded_at
    
    p = Path(path)
    if not p.exists():
        return {}
    
    # Prüfe mtime und TTL
    try:
        current_mtime = p.stat().st_mtime
        now = time.time()
        
        if (_cache_registry is not None and 
            current_mtime == _cache_registry_mtime and 
            (now - _cache_registry_loaded_at) < _CACHE_TTL):
            return _cache_registry
        
        # Reload
        data = json.loads(p.read_text(encoding="utf-8") or "{}")
        _cache_registry = data
        _cache_registry_mtime = current_mtime
        _cache_registry_loaded_at = now
        return data
    except Exception as e:
        logger.error(f"Fehler beim Laden von Registry: {e}", extra={"path": path})
        return {}

def _preset_from_request(data: Dict[str, Any], default: str) -> str:
    md = data.get("metadata")
    if isinstance(md, dict):
        v = md.get("ai_shield_preset") or md.get("preset")
        if isinstance(v, str) and v.strip():
            return v.strip()
    return default

def _score_injection(text: str) -> int:
    low = (text or "").lower()
    score = 0
    for pat in INJECTION_SIGNALS:
        if re.search(pat, low, flags=re.IGNORECASE):
            score += 2
    if "```" in (text or ""):
        score += 1
    if "system prompt" in low or "developer message" in low:
        score += 1
    return score

def _mask_text(text: str, email_mode: str, phone_mode: str, cc_mode: str) -> str:
    out = text
    if email_mode == "mask":
        out = EMAIL_RE.sub("<EMAIL_ADDRESS>", out)
    if phone_mode == "mask":
        out = PHONE_RE.sub("<PHONE_NUMBER>", out)
    if cc_mode == "mask":
        for raw in _find_credit_cards(out):
            out = out.replace(raw, "<CREDIT_CARD>")
    return out

def _server_id_from_tool(tool_def: Dict[str, Any]) -> Optional[str]:
    for k in ("server_label", "server_id", "server_name", "server"):
        v = tool_def.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

class AIShieldCallback(CustomLogger):
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
        ],
    ):
        """
        Pre-Call Hook mit Policy Engine Integration.
        Fail-Closed Strategie: Bei Fehlern wird blockiert (sicherheitsorientiert).
        """
        try:
            # Import Policy Engine (lazy import to avoid circular deps)
            from policy_engine import get_policy_engine, Decision
            
            engine = get_policy_engine()
            
            # Ensure metadata exists
            md = data.get("metadata")
            if not isinstance(md, dict):
                md = {}
            data["metadata"] = md
            
            # Run policy engine decision
            decision = engine.decide(data)
            
            # Store correlation_id in metadata for response headers
            if decision.correlation_id:
                md["correlation_id"] = decision.correlation_id
                md["ai_shield_request_id"] = decision.correlation_id
            
            # Apply decision based on compatibility mode
            if decision.decision == Decision.BLOCK:
                reason_msg = ", ".join(decision.reason_codes) if decision.reason_codes else "Policy violation"
                logger.warning(
                    "AI-Shield: Blockiert",
                    extra={
                        "event": "policy_block",
                        "correlation_id": decision.correlation_id,
                        "tenant_id": decision.tenant_id,
                        "reason_codes": decision.reason_codes,
                        "rule_triggers": decision.rule_triggers,
                    }
                )
                return f"AI-Shield: Blockiert ({reason_msg})."
            
            # Apply sanitized request if available
            if decision.sanitized_request:
                data.update(decision.sanitized_request)
            
            # Log warn decisions
            if decision.decision == Decision.WARN:
                logger.info(
                    "AI-Shield: Warn",
                    extra={
                        "event": "policy_warn",
                        "correlation_id": decision.correlation_id,
                        "tenant_id": decision.tenant_id,
                        "reason_codes": decision.reason_codes,
                        "rule_triggers": decision.rule_triggers,
                    }
                )
                # Add warning to metadata (can be used in response headers)
                if "warnings" not in md:
                    md["warnings"] = []
                md["warnings"].append({
                    "type": "policy_warn",
                    "reason_codes": decision.reason_codes,
                })
            
            # Legacy MCP tool permission checks (keep for backward compatibility)
            policies_path = os.environ.get("AI_SHIELD_POLICY_PATH", "/app/policies/presets.yaml")
            policies = _load_yaml(policies_path)
            default_preset = os.environ.get("AI_SHIELD_PRESET_DEFAULT", policies.get("default_preset", "public_website"))
            preset = _preset_from_request(data, default_preset)
            preset_cfg = ((policies.get("presets") or {}).get(preset) or {}) if isinstance(policies, dict) else {}
            mcp_cfg = preset_cfg.get("mcp") or {}
            
            risky_pat = mcp_cfg.get("risky_tool_name_regex")
            risky_re = re.compile(str(risky_pat)) if risky_pat else None

            registry_path = os.environ.get("AI_SHIELD_REGISTRY_PATH", "/app/control-plane-data/mcp_registry.json")
            registry = _load_registry(registry_path)
            servers = (registry.get("servers") or {}) if isinstance(registry, dict) else {}

            auto_requires_allowlist = bool(mcp_cfg.get("auto_approve_requires_allowlist", True))

            if isinstance(data.get("tools"), list):
                for t in data["tools"]:
                    if not isinstance(t, dict):
                        continue
                    if t.get("type") != "mcp":
                        continue
                    if str(t.get("require_approval", "")).lower() != "never":
                        continue
                    allowed_tools = t.get("allowed_tools")
                    if not isinstance(allowed_tools, list) or len(allowed_tools) == 0:
                        t.pop("require_approval", None)
                        continue
                    if risky_re and any(risky_re.search(str(x or "")) for x in allowed_tools):
                        t.pop("require_approval", None)
                        continue
                    if auto_requires_allowlist:
                        sid = _server_id_from_tool(t)
                        if not sid:
                            t.pop("require_approval", None)
                            continue
                        if not isinstance(servers, dict):
                            t.pop("require_approval", None)
                            continue
                        scfg = servers.get(sid)
                        if not isinstance(scfg, dict):
                            t.pop("require_approval", None)
                            continue
                        auto_ok = scfg.get("auto_approve_tools")
                        if not isinstance(auto_ok, list) or len(auto_ok) == 0:
                            t.pop("require_approval", None)
                            continue
                        if any((not isinstance(x, str)) or (x not in auto_ok) for x in allowed_tools):
                            t.pop("require_approval", None)
                            continue

            return data
        except Exception as e:
            # Fail-closed: Bei unerwarteten Fehlern blockieren (sicherheitsorientiert)
            logger.error(f"AI-Shield: Fehler im pre-call hook: {e}", exc_info=True)
            return "AI-Shield: Blockiert (Interner Fehler)."

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        """Post-Call Hook: Add correlation_id to response if possible"""
        try:
            md = data.get("metadata", {})
            correlation_id = md.get("correlation_id") or md.get("ai_shield_request_id")
            
            if correlation_id and hasattr(response, "headers"):
                # Add correlation_id to response headers for observability
                if not hasattr(response, "headers") or not isinstance(response.headers, dict):
                    response.headers = {}
                response.headers["X-Correlation-ID"] = correlation_id
                
                # Add warnings if present
                warnings = md.get("warnings")
                if warnings:
                    import json
                    response.headers["X-AI-Shield-Warnings"] = json.dumps(warnings)
        except Exception:
            pass  # Non-critical, don't fail on header addition
        
        return response

    async def async_post_call_failure_hook(
        self,
        request_data: dict,
        original_exception: Exception,
        user_api_key_dict: UserAPIKeyAuth,
        traceback_str: Optional[str] = None,
    ):
        return

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
        request_data: dict,
    ) -> AsyncGenerator[ModelResponseStream, None]:
        async for item in response:
            yield item

ai_shield_callback = AIShieldCallback()
