import os
import re
import json
import time
import uuid
from typing import Any, AsyncGenerator, Dict, Literal, Optional

import yaml
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import DualCache, UserAPIKeyAuth
from litellm.types.utils import ModelResponseStream


def _epoch() -> int:
    return int(time.time())


_SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "sk-REDACTED"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"), "gh-REDACTED"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AKIA-REDACTED"),
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "ASIA-REDACTED"),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), "AIza-REDACTED"),
]

_INJECTION_SIGNALS = [
    r"ignore (all|any|previous) (instructions|system|developer)",
    r"disregard (all|any|previous) (instructions|system|developer)",
    r"reveal (the )?(system|developer) (prompt|message)",
    r"print (the )?(system|developer) prompt",
    r"show me (the )?(system|developer) (prompt|message)",
    r"jailbreak",
    r"do anything now",
    r"developer mode",
    r"BEGIN[\s\S]{0,200}PROMPT[\s\S]{0,200}INJECTION",
]


def _redact_secrets(text: str) -> str:
    out = text
    for rgx, repl in _SECRET_PATTERNS:
        out = rgx.sub(repl, out)
    return out


def _extract_text(data: Dict[str, Any]) -> str:
    if isinstance(data.get("messages"), list):
        parts = []
        for m in data["messages"]:
            if not isinstance(m, dict):
                continue
            c = m.get("content")
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, list):
                for p in c:
                    if isinstance(p, dict) and p.get("type") == "text" and isinstance(p.get("text"), str):
                        parts.append(p["text"])
        return "\n".join(parts)
    if isinstance(data.get("input"), str):
        return data["input"]
    return ""


def _score_injection(text: str) -> int:
    t = text or ""
    score = 0
    low = t.lower()
    for pat in _INJECTION_SIGNALS:
        if re.search(pat, low, flags=re.IGNORECASE):
            score += 2
    if "```" in t:
        score += 1
    if "system prompt" in low or "developer message" in low:
        score += 1
    if "ignore" in low and "tool" in low:
        score += 1
    return score


class AIShieldHandler(CustomLogger):
    def __init__(self) -> None:
        self.policy_path = os.environ.get("AI_SHIELD_POLICY_PATH", "/app/policies/presets.yaml")
        self.default_preset = os.environ.get("AI_SHIELD_PRESET_DEFAULT", "public_website")
        self._presets = {}
        self._load_policies()

    def _load_policies(self) -> None:
        try:
            with open(self.policy_path, "r", encoding="utf-8") as f:
                obj = yaml.safe_load(f) or {}
            presets = obj.get("presets", {})
            if isinstance(presets, dict):
                self._presets = presets
        except Exception:
            self._presets = {}

    def _get_preset(self, user_api_key_dict: UserAPIKeyAuth, data: Dict[str, Any]) -> str:
        preset = None
        meta = None
        try:
            meta = getattr(user_api_key_dict, "metadata", None)
        except Exception:
            meta = None
        if isinstance(meta, dict):
            preset = meta.get("ai_shield_preset") or meta.get("preset")
        if not preset:
            md = data.get("metadata")
            if isinstance(md, dict):
                preset = md.get("ai_shield_preset")
        if not preset:
            preset = self.default_preset
        return str(preset)

    def _threshold(self, preset: str) -> int:
        cfg = self._presets.get(preset, {})
        if isinstance(cfg, dict):
            v = cfg.get("injection_block_threshold")
            if isinstance(v, int):
                return v
        return 6

    def _redact_output_enabled(self, preset: str) -> bool:
        cfg = self._presets.get(preset, {})
        if isinstance(cfg, dict):
            v = cfg.get("redact_output_secrets")
            if isinstance(v, bool):
                return v
        return True

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal["completion", "text_completion", "embeddings", "image_generation", "moderation", "audio_transcription"],
    ):
        preset = self._get_preset(user_api_key_dict=user_api_key_dict, data=data)
        req_id = None
        md = data.get("metadata")
        if isinstance(md, dict):
            req_id = md.get("ai_shield_request_id")
        if not req_id:
            req_id = str(uuid.uuid4())
        if not isinstance(md, dict):
            md = {}
        md["ai_shield_request_id"] = req_id
        md["ai_shield_preset"] = preset
        data["metadata"] = md

        if not data.get("user"):
            u = None
            try:
                u = getattr(user_api_key_dict, "user_id", None) or getattr(user_api_key_dict, "team_id", None)
            except Exception:
                u = None
            data["user"] = str(u) if u else "unknown"

        text = _extract_text(data)
        score = _score_injection(text)
        threshold = self._threshold(preset)

        audit = {
            "ts": _epoch(),
            "event": "pre_call",
            "request_id": req_id,
            "preset": preset,
            "call_type": call_type,
            "injection_score": score,
            "threshold": threshold,
        }
        print(json.dumps(audit, ensure_ascii=False))

        if score >= threshold:
            return "Request blockiert: Verdacht auf Prompt-Injection. Bitte formuliere die Anfrage ohne versteckte Instruktionen."

        if isinstance(data.get("messages"), list):
            new_messages = []
            for m in data["messages"]:
                if not isinstance(m, dict):
                    new_messages.append(m)
                    continue
                c = m.get("content")
                if isinstance(c, str):
                    m2 = dict(m)
                    m2["content"] = _redact_secrets(c)
                    new_messages.append(m2)
                else:
                    new_messages.append(m)
            data["messages"] = new_messages

        if isinstance(data.get("input"), str):
            data["input"] = _redact_secrets(data["input"])

        return data

    async def async_post_call_success_hook(self, data: dict, user_api_key_dict: UserAPIKeyAuth, response):
        preset = self._get_preset(user_api_key_dict=user_api_key_dict, data=data)
        req_id = None
        md = data.get("metadata")
        if isinstance(md, dict):
            req_id = md.get("ai_shield_request_id")
        audit = {
            "ts": _epoch(),
            "event": "post_call_success",
            "request_id": req_id,
            "preset": preset,
        }
        print(json.dumps(audit, ensure_ascii=False))

        if not self._redact_output_enabled(preset):
            return response

        try:
            if isinstance(response, dict):
                r = dict(response)
                if isinstance(r.get("choices"), list):
                    choices = []
                    for ch in r["choices"]:
                        if isinstance(ch, dict) and isinstance(ch.get("message"), dict):
                            msg = dict(ch["message"])
                            if isinstance(msg.get("content"), str):
                                msg["content"] = _redact_secrets(msg["content"])
                            ch2 = dict(ch)
                            ch2["message"] = msg
                            choices.append(ch2)
                        else:
                            choices.append(ch)
                    r["choices"] = choices
                return r
        except Exception:
            return response

        return response

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
        request_data: dict,
    ) -> AsyncGenerator[ModelResponseStream, None]:
        async for item in response:
            yield item


ai_shield_handler = AIShieldHandler()
