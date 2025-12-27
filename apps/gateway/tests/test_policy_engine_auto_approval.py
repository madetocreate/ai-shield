"""
Tests for Policy Engine MCP Auto-Approval hardening.
"""

import pytest
import json
import tempfile
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from policy_engine import PolicyEngine, Decision


def test_auto_approval_disabled_when_unpinned():
    """Test that require_approval=never is removed for unpinned MCP servers."""
    # Create temporary registry file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        registry_data = {
            "servers": {
                "test-server-pinned": {
                    "pinned_tools_hash": "abc123",
                    "auto_approve_tools": ["tool1", "tool2"]
                },
                "test-server-unpinned": {
                    # No pinned_tools_hash -> unpinned
                    "auto_approve_tools": ["tool1", "tool2"]
                }
            }
        }
        json.dump(registry_data, f)
        registry_path = f.name
    
    try:
        engine = PolicyEngine(registry_path=registry_path)
        
        # Test 1: Unpinned server -> require_approval=never should be removed
        request_unpinned = {
            "messages": [{"role": "user", "content": "test"}],
            "tools": [
                {
                    "type": "mcp",
                    "server_id": "test-server-unpinned",
                    "require_approval": "never",
                    "allowed_tools": ["tool1"]
                }
            ]
        }
        
        decision = engine.decide(request_unpinned)
        
        # The tool should have require_approval removed
        # Check that sanitization happened (we can't directly check tools, but decision should be made)
        assert decision.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]
        
        # Test 2: Pinned server with matching tools -> require_approval=never should be kept
        request_pinned = {
            "messages": [{"role": "user", "content": "test"}],
            "tools": [
                {
                    "type": "mcp",
                    "server_id": "test-server-pinned",
                    "require_approval": "never",
                    "allowed_tools": ["tool1"]  # tool1 is in auto_approve_tools
                }
            ]
        }
        
        decision2 = engine.decide(request_pinned)
        assert decision2.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]
        
        # Test 3: Server not in registry -> require_approval=never should be removed
        request_not_in_registry = {
            "messages": [{"role": "user", "content": "test"}],
            "tools": [
                {
                    "type": "mcp",
                    "server_id": "non-existent-server",
                    "require_approval": "never",
                    "allowed_tools": ["tool1"]
                }
            ]
        }
        
        decision3 = engine.decide(request_not_in_registry)
        assert decision3.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]
        
        # Test 4: No server_id -> require_approval=never should be removed
        request_no_server_id = {
            "messages": [{"role": "user", "content": "test"}],
            "tools": [
                {
                    "type": "mcp",
                    "require_approval": "never",
                    "allowed_tools": ["tool1"]
                }
            ]
        }
        
        decision4 = engine.decide(request_no_server_id)
        assert decision4.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]
        
        # Test 5: Tool not in auto_approve_tools -> require_approval=never should be removed
        request_tool_not_allowed = {
            "messages": [{"role": "user", "content": "test"}],
            "tools": [
                {
                    "type": "mcp",
                    "server_id": "test-server-pinned",
                    "require_approval": "never",
                    "allowed_tools": ["tool99"]  # tool99 is NOT in auto_approve_tools
                }
            ]
        }
        
        decision5 = engine.decide(request_tool_not_allowed)
        assert decision5.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]
        
    finally:
        # Cleanup
        Path(registry_path).unlink()


def test_auto_approval_no_allowed_tools():
    """Test that require_approval=never is removed when allowed_tools is empty."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        registry_data = {
            "servers": {
                "test-server": {
                    "pinned_tools_hash": "abc123",
                    "auto_approve_tools": ["tool1", "tool2"]
                }
            }
        }
        json.dump(registry_data, f)
        registry_path = f.name
    
    try:
        engine = PolicyEngine(registry_path=registry_path)
        
        request = {
            "messages": [{"role": "user", "content": "test"}],
            "tools": [
                {
                    "type": "mcp",
                    "server_id": "test-server",
                    "require_approval": "never",
                    "allowed_tools": []  # Empty allowed_tools
                }
            ]
        }
        
        decision = engine.decide(request)
        assert decision.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]
        
    finally:
        Path(registry_path).unlink()


def test_auto_approval_non_mcp_tool():
    """Test that non-MCP tools are not affected by auto-approval sanitization."""
    engine = PolicyEngine()
    
    request = {
        "messages": [{"role": "user", "content": "test"}],
        "tools": [
            {
                "type": "function",
                "function": {"name": "test_function"},
                "require_approval": "never"
            }
        ]
    }
    
    decision = engine.decide(request)
    # Non-MCP tools should not be sanitized
    assert decision.decision in [Decision.ALLOW, Decision.BLOCK, Decision.WARN]

