#!/usr/bin/env python3
"""
Test-Runner für Agent-Tests

Führt alle Tests aus und gibt detailliertes Feedback.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Führt Tests aus"""
    test_dir = Path(__file__).parent.parent / "tests"
    
    if not test_dir.exists():
        print("❌ Test-Verzeichnis nicht gefunden")
        return 1
    
    print("🧪 Führe Agent-Tests aus...")
    print("=" * 60)
    print()
    
    # Pytest ausführen
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(test_dir),
            "-v",
            "--tb=short",
            "--color=yes"
        ],
        capture_output=False
    )
    
    print()
    print("=" * 60)
    
    if result.returncode == 0:
        print("✅ Alle Tests bestanden!")
        return 0
    else:
        print("❌ Einige Tests fehlgeschlagen")
        return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
