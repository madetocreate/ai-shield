"""
Optional: LLM Guard Integration für erweiterte Sicherheitsprüfungen.

Diese Datei kann als zusätzlicher Callback verwendet werden, wenn LLM Guard installiert ist.
Aktivierung in config.yaml:
  callbacks: [custom_callbacks.ai_shield_callback, custom_callbacks_llm_guard.llm_guard_callback]
"""

import os
import logging
from typing import Any, Dict, Optional

try:
    from llm_guard.input_scanners import PromptInjection, Toxicity, Anonymize
    from llm_guard.output_scanners import NoRefusal, Regex, Sensitive
    LLM_GUARD_AVAILABLE = True
except ImportError:
    LLM_GUARD_AVAILABLE = False

from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache

# Logger für strukturiertes Logging
logger = logging.getLogger(__name__)

if LLM_GUARD_AVAILABLE:
    input_scanner = PromptInjection()
    toxicity_scanner = Toxicity()
    output_scanner = NoRefusal()

class LLMGuardCallback(CustomLogger):
    """Erweiterte Sicherheitsprüfungen mit LLM Guard."""
    
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: str,
    ):
        if not LLM_GUARD_AVAILABLE:
            return data
        
        # Extrahiere Text aus Messages
        msg_texts = []
        if isinstance(data.get("messages"), list):
            for m in data["messages"]:
                if isinstance(m, dict) and isinstance(m.get("content"), str):
                    msg_texts.append(m["content"])
        joined = "\n".join(msg_texts)
        
        if not joined:
            return data
        
        # Prompt Injection Scan
        try:
            scan_result = input_scanner.scan(joined)
            if not scan_result.is_valid:
                return f"AI-Shield (LLM Guard): Blockiert - {scan_result.risky_value}"
        except Exception:
            pass  # Fallback auf Standard-Callback
        
        # Toxicity Scan (optional)
        if os.environ.get("AI_SHIELD_ENABLE_TOXICITY_CHECK", "false").lower() == "true":
            try:
                tox_result = toxicity_scanner.scan(joined)
                if not tox_result.is_valid:
                    return f"AI-Shield (LLM Guard): Blockiert - Toxischer Inhalt erkannt"
            except Exception:
                pass
        
        return data
    
    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        if not LLM_GUARD_AVAILABLE:
            return response
        
        # Output Scanning (optional)
        if os.environ.get("AI_SHIELD_ENABLE_OUTPUT_SCAN", "false").lower() == "true":
            try:
                # Extrahiere Response-Text
                response_text = ""
                if hasattr(response, "choices") and response.choices:
                    if hasattr(response.choices[0], "message"):
                        response_text = response.choices[0].message.get("content", "")
                
                if response_text:
                    scan_result = output_scanner.scan(response_text)
                    if not scan_result.is_valid:
                        # Logge aber blockiere nicht (Post-Call)
                        logger.warning(
                            "LLM Guard Output Warning",
                            extra={
                                "event": "llm_guard_output_warning",
                                "risky_value": scan_result.risky_value,
                                "is_valid": scan_result.is_valid,
                            }
                        )
            except Exception as e:
                logger.debug(f"LLM Guard output scan error: {e}", exc_info=True)
        
        return response

if LLM_GUARD_AVAILABLE:
    llm_guard_callback = LLMGuardCallback()
else:
    llm_guard_callback = None

