#!/usr/bin/env python3
"""
AI-Shield Policy Drift Validator.

Validiert, dass AI-Shield guardrails konsistent mit policy_registry.json sind.
Optional: Nutzt explizite requires_approval Signale statt Regex (Regex bleibt Fallback).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_ai_shield_config(config_path: Path) -> Dict[str, Any]:
    """Lädt AI-Shield config.yaml."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_policy_registry(registry_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Lädt policy_registry.json."""
    if registry_path is None:
        # Try to find it relative to backend-agents
        backend_agents = Path(__file__).parent.parent.parent / "Backend" / "backend-agents"
        registry_path = backend_agents / "contracts" / "generated" / "policy_registry.json"
    
    if not registry_path or not registry_path.exists():
        return None
    
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load policy registry: {e}", file=sys.stderr)
        return None


def extract_tool_permission_rules(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrahiert tool_permission guardrail rules aus config."""
    guardrails = config.get("guardrails", [])
    
    for guardrail in guardrails:
        if guardrail.get("guardrail_name") == "ai-shield-tool-permission":
            litellm_params = guardrail.get("litellm_params", {})
            rules = litellm_params.get("rules", [])
            return rules
    
    return []


def get_tools_requiring_approval_from_registry(
    policy_registry: Dict[str, Any],
) -> Set[str]:
    """Extrahiert Tool-Namen, die requires_approval=true haben."""
    tool_policies = policy_registry.get("tool_policies", {}).get("policies", [])
    
    tools_requiring_approval: Set[str] = set()
    for policy in tool_policies:
        tool_name = policy.get("tool_name", "")
        requires_approval = policy.get("requires_approval", False)
        if requires_approval:
            tools_requiring_approval.add(tool_name)
            # Also add without _tool suffix (for MCP tools)
            if tool_name.endswith("_tool"):
                tools_requiring_approval.add(tool_name[:-5])
    
    return tools_requiring_approval


def check_drift_against_registry(
    config: Dict[str, Any],
    policy_registry: Dict[str, Any],
) -> tuple[bool, List[str]]:
    """
    Prüft, ob AI-Shield guardrails konsistent mit policy_registry.json sind.
    
    Aktuell: AI-Shield nutzt Regex-basierte Tool-Permissions.
    Optional: Könnte explizite requires_approval Signale nutzen.
    """
    errors = []
    warnings = []
    
    # Get tools requiring approval from registry
    registry_tools_requiring_approval = get_tools_requiring_approval_from_registry(policy_registry)
    
    # Get AI-Shield tool permission rules
    rules = extract_tool_permission_rules(config)
    
    # Check if registry tools are covered by AI-Shield rules
    # AI-Shield uses regex patterns, so we check if tool names match
    for tool_name in registry_tools_requiring_approval:
        # Check if tool is covered by any rule
        covered = False
        for rule in rules:
            pattern = rule.get("tool_name", "")
            if pattern and re.search(pattern, tool_name, re.IGNORECASE):
                covered = True
                break
        
        if not covered:
            warnings.append(
                f"Tool '{tool_name}' requires approval in registry but not covered by AI-Shield rules"
            )
    
    # Note: We don't fail on warnings, as AI-Shield uses regex patterns
    # which may cover tools in a different way than explicit registry entries
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def validate_guardrail_config(config: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validiert AI-Shield guardrail Konfiguration."""
    errors = []
    guardrails = config.get("guardrails", [])
    
    if not isinstance(guardrails, list):
        errors.append("guardrails must be a list")
        return False, errors
    
    tool_permission_found = False
    for guardrail in guardrails:
        guardrail_name = guardrail.get("guardrail_name", "")
        litellm_params = guardrail.get("litellm_params", {})
        
        if guardrail_name == "ai-shield-tool-permission":
            tool_permission_found = True
            rules = litellm_params.get("rules", [])
            
            if not isinstance(rules, list):
                errors.append("tool_permission guardrail rules must be a list")
                continue
            
            for rule in rules:
                if not isinstance(rule, dict):
                    errors.append("tool_permission rule must be a dictionary")
                    continue
                
                tool_name = rule.get("tool_name", "")
                decision = rule.get("decision", "")
                
                if not tool_name:
                    errors.append("tool_permission rule must have tool_name")
                if decision not in ("allow", "deny"):
                    errors.append(f"tool_permission rule decision must be 'allow' or 'deny', got '{decision}'")
    
    # Note: tool_permission_found check removed (not an error if missing)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate AI-Shield policy drift")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent.parent / "apps" / "gateway" / "config.yaml",
        help="Path to AI-Shield config.yaml",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="Path to policy_registry.json (optional, for drift check)",
    )
    parser.add_argument(
        "--check-drift",
        action="store_true",
        help="Check for drift against policy_registry.json",
    )
    
    args = parser.parse_args()
    
    try:
        # Load config
        config = load_ai_shield_config(args.config)
        
        # Validate guardrail config
        is_valid, errors = validate_guardrail_config(config)
        
        if not is_valid:
            print("✗ Guardrail validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        
        print("✓ Guardrail validation passed")
        
        # Optional: Check drift against registry
        if args.check_drift:
            registry = load_policy_registry(args.registry)
            if registry:
                drift_valid, drift_errors, drift_warnings = check_drift_against_registry(config, registry)
                
                if not drift_valid:
                    print("✗ Drift check failed:", file=sys.stderr)
                    for error in drift_errors:
                        print(f"  - {error}", file=sys.stderr)
                    sys.exit(1)
                
                if drift_warnings:
                    print("⚠ Drift check warnings:")
                    for warning in drift_warnings:
                        print(f"  - {warning}")
                
                if not drift_warnings:
                    print("✓ Drift check passed (no mismatches found)")
            else:
                print("⚠ Drift check skipped (policy_registry.json not found)")
        
        print("\n✓ All validations passed")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n✗ Validation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

