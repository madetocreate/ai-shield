"""
Tests für AI-Shield Policy Drift Validator.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_policy_drift import (
    load_ai_shield_config,
    extract_tool_permission_rules,
    get_tools_requiring_approval_from_registry,
    check_drift_against_registry,
    validate_guardrail_config,
)


class TestValidatePolicyDrift:
    """Tests für Policy Drift Validator."""

    def test_extract_tool_permission_rules(self):
        """Test: Extrahiert tool_permission rules."""
        config = {
            "guardrails": [
                {
                    "guardrail_name": "ai-shield-tool-permission",
                    "litellm_params": {
                        "guardrail": "tool_permission",
                        "rules": [
                            {
                                "id": "deny_destructive_tools",
                                "tool_name": "(?i).*(delete|remove).*",
                                "decision": "deny",
                            },
                        ],
                    },
                },
            ],
        }
        
        rules = extract_tool_permission_rules(config)
        assert len(rules) == 1
        assert rules[0]["tool_name"] == "(?i).*(delete|remove).*"

    def test_get_tools_requiring_approval_from_registry(self):
        """Test: Extrahiert Tools, die Approval benötigen."""
        policy_registry = {
            "tool_policies": {
                "policies": [
                    {
                        "tool_name": "crm_upsert_contact_tool",
                        "requires_approval": True,
                    },
                    {
                        "tool_name": "memory_delete",
                        "requires_approval": True,
                    },
                    {
                        "tool_name": "memory_search",
                        "requires_approval": False,
                    },
                ],
            },
        }
        
        tools = get_tools_requiring_approval_from_registry(policy_registry)
        assert "crm_upsert_contact_tool" in tools
        assert "crm_upsert_contact" in tools  # Without _tool suffix
        assert "memory_delete" in tools
        assert "memory_search" not in tools

    def test_validate_guardrail_config(self):
        """Test: Validiert guardrail Konfiguration."""
        config = {
            "guardrails": [
                {
                    "guardrail_name": "ai-shield-tool-permission",
                    "litellm_params": {
                        "guardrail": "tool_permission",
                        "rules": [
                            {
                                "id": "deny_destructive_tools",
                                "tool_name": "(?i).*(delete|remove).*",
                                "decision": "deny",
                            },
                        ],
                    },
                },
            ],
        }
        
        is_valid, errors = validate_guardrail_config(config)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_guardrail_config(self):
        """Test: Validiert ungültige guardrail Konfiguration."""
        config = {
            "guardrails": [
                {
                    "guardrail_name": "ai-shield-tool-permission",
                    "litellm_params": {
                        "guardrail": "tool_permission",
                        "rules": [
                            {
                                "id": "deny_destructive_tools",
                                # Missing tool_name
                                "decision": "deny",
                            },
                        ],
                    },
                },
            ],
        }
        
        is_valid, errors = validate_guardrail_config(config)
        assert is_valid is False
        assert any("tool_name" in error.lower() for error in errors)

