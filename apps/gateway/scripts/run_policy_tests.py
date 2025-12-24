#!/usr/bin/env python3
"""
Policy Test Harness - Führt alle Policy-Tests aus und vergleicht mit Expected Results

Usage:
    python scripts/run_policy_tests.py
    python scripts/run_policy_tests.py --pack kmu_standard
    python scripts/run_policy_tests.py --test test_pii_detection
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add gateway to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from policy_engine import get_policy_engine, Decision


def load_test_file(test_path: Path) -> Dict[str, Any]:
    """Lade Test-Datei"""
    try:
        with open(test_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Fehler beim Laden von {test_path}: {e}", file=sys.stderr)
        return {"test_cases": []}


def load_expected_file(expected_path: Path) -> Dict[str, Any]:
    """Lade Expected-Datei"""
    try:
        with open(expected_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"test_cases": []}


def normalize_decision(decision: Decision) -> str:
    """Normalisiere Decision zu String"""
    return decision.value


def compare_results(actual: Dict[str, Any], expected: Dict[str, Any], test_name: str) -> List[str]:
    """Vergleiche tatsächliche und erwartete Ergebnisse, retourniere Fehlerliste"""
    errors = []
    
    # Decision check
    actual_decision = normalize_decision(actual.get("decision"))
    expected_decision = expected.get("decision")
    if actual_decision != expected_decision:
        errors.append(
            f"  Decision mismatch: expected '{expected_decision}', got '{actual_decision}'"
        )
    
    # Reason codes check (order doesn't matter)
    actual_reasons = set(actual.get("reason_codes", []))
    expected_reasons = set(expected.get("reason_codes", []))
    if actual_reasons != expected_reasons:
        errors.append(
            f"  Reason codes mismatch: expected {sorted(expected_reasons)}, got {sorted(actual_reasons)}"
        )
    
    # Sanitized check (if expected)
    if expected.get("has_sanitized") and not actual.get("sanitized_request"):
        errors.append("  Expected sanitized request, but none was returned")
    
    return errors


def run_test_suite(test_file: Path, expected_dir: Path, pack_name: Optional[str] = None) -> tuple[int, int]:
    """Führe Test-Suite aus"""
    test_data = load_test_file(test_file)
    test_cases = test_data.get("test_cases", [])
    
    if not test_cases:
        print(f"WARNING: Keine Test-Cases in {test_file}", file=sys.stderr)
        return 0, 0
    
    # Load expected results
    test_name = test_file.stem
    expected_file = expected_dir / pack_name / f"{test_name}.json" if pack_name else expected_dir / f"{test_name}.json"
    expected_data = load_expected_file(expected_file)
    expected_map = {tc["name"]: tc["expected"] for tc in expected_data.get("test_cases", [])}
    
    engine = get_policy_engine()
    
    passed = 0
    failed = 0
    
    print(f"\nRunning test suite: {test_file.name}")
    print("=" * 60)
    
    for test_case in test_cases:
        test_name = test_case.get("name", "unnamed")
        input_data = test_case.get("input", {})
        expected = test_case.get("expected") or expected_map.get(test_name, {})
        
        if not expected:
            print(f"SKIP: {test_name} (no expected result)")
            continue
        
        # Run policy engine
        try:
            decision = engine.decide(input_data)
            actual = {
                "decision": decision.decision,
                "reason_codes": decision.reason_codes,
                "sanitized_request": decision.sanitized_request,
            }
            
            # Compare
            errors = compare_results(actual, expected, test_name)
            
            if errors:
                failed += 1
                print(f"FAIL: {test_name}")
                for error in errors:
                    print(error)
                print(f"  Input: {json.dumps(input_data, indent=2)}")
                print(f"  Expected: {json.dumps(expected, indent=2)}")
                print(f"  Actual: {json.dumps(actual, indent=2)}")
            else:
                passed += 1
                print(f"PASS: {test_name}")
        
        except Exception as e:
            failed += 1
            print(f"ERROR: {test_name} - {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
    
    return passed, failed


def main():
    parser = argparse.ArgumentParser(description="Run policy tests")
    parser.add_argument("--pack", help="Test only specific pack", default=None)
    parser.add_argument("--test", help="Test only specific test file", default=None)
    args = parser.parse_args()
    
    gateway_dir = Path(__file__).parent.parent
    tests_dir = gateway_dir / "policies" / "tests"
    expected_dir = gateway_dir / "policies" / "expected"
    
    if not tests_dir.exists():
        print(f"ERROR: Tests directory not found: {tests_dir}", file=sys.stderr)
        sys.exit(1)
    
    test_files = list(tests_dir.glob("*.json"))
    if args.test:
        test_files = [f for f in test_files if f.stem == args.test]
    
    if not test_files:
        print("No test files found", file=sys.stderr)
        sys.exit(1)
    
    total_passed = 0
    total_failed = 0
    
    for test_file in sorted(test_files):
        if args.pack:
            # Test specific pack
            passed, failed = run_test_suite(test_file, expected_dir, args.pack)
        else:
            # Test all packs
            packs = [d.name for d in expected_dir.iterdir() if d.is_dir()]
            for pack in packs:
                passed, failed = run_test_suite(test_file, expected_dir, pack)
                total_passed += passed
                total_failed += failed
            continue
        
        total_passed += passed
        total_failed += failed
    
    print("\n" + "=" * 60)
    print(f"Summary: {total_passed} passed, {total_failed} failed")
    
    if total_failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

