import os
import re
import json
import time
import uuid
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
    if yaml is None:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

def _load_registry(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8") or "{}")
    except Exception:
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
        policies = _load_yaml(os.environ.get("AI_SHIELD_POLICY_PATH", "/app/policies/presets.yaml"))
        default_preset = os.environ.get("AI_SHIELD_PRESET_DEFAULT", policies.get("default_preset", "public_website"))
        preset = _preset_from_request(data, default_preset)
        preset_cfg = ((policies.get("presets") or {}).get(preset) or {}) if isinstance(policies, dict) else {}
        pii_cfg = preset_cfg.get("pii") or {}
        mcp_cfg = preset_cfg.get("mcp") or {}

        md = data.get("metadata")
        if not isinstance(md, dict):
            md = {}
        if "ai_shield_request_id" not in md:
            md["ai_shield_request_id"] = str(uuid.uuid4())
        md["ai_shield_preset"] = preset
        data["metadata"] = md

        msg_texts: List[str] = []
        if isinstance(data.get("messages"), list):
            for m in data["messages"]:
                if isinstance(m, dict) and isinstance(m.get("content"), str):
                    msg_texts.append(m["content"])
        joined = "\n".join(msg_texts)

        thr = int(preset_cfg.get("injection_block_threshold", 6)) if isinstance(preset_cfg, dict) else 6
        inj_score = _score_injection(joined)

        audit = {
            "ts": _epoch(),
            "event": "pre_call",
            "request_id": md.get("ai_shield_request_id"),
            "preset": preset,
            "call_type": call_type,
            "injection_score": inj_score,
            "threshold": thr,
        }
        print(json.dumps(audit, ensure_ascii=False))

        if inj_score >= thr:
            return "AI-Shield: Blockiert (Verdacht auf Prompt-Injection)."

        email_mode = str(pii_cfg.get("email", "mask")).lower()
        phone_mode = str(pii_cfg.get("phone", "mask")).lower()
        cc_mode = str(pii_cfg.get("credit_card", "block")).lower()

        if cc_mode == "block":
            if _find_credit_cards(joined):
                return "AI-Shield: Blockiert (Kreditkartennummer erkannt)."

        if isinstance(data.get("messages"), list):
            for m in data["messages"]:
                if isinstance(m, dict) and isinstance(m.get("content"), str):
                    m["content"] = _mask_text(m["content"], email_mode, phone_mode, cc_mode)

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
                    # Fail-closed: require approval if server_id is missing
                    if not sid:
                        t.pop("require_approval", None)
                        continue
                    # Fail-closed: require approval if server config is missing
                    if not isinstance(servers, dict):
                        t.pop("require_approval", None)
                        continue
                    scfg = servers.get(sid)
                    if not isinstance(scfg, dict):
                        t.pop("require_approval", None)
                        continue
                    # Fail-closed: require approval if auto_approve_tools is missing or empty
                    auto_ok = scfg.get("auto_approve_tools")
                    if not isinstance(auto_ok, list) or len(auto_ok) == 0:
                        t.pop("require_approval", None)
                        continue
                    # Only allow if all allowed_tools are in auto_approve_tools
                    if any((not isinstance(x, str)) or (x not in auto_ok) for x in allowed_tools):
                        t.pop("require_approval", None)
                        continue

        return data

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
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
