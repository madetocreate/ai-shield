#!/usr/bin/env python3
"""
Production Readiness Check Script

Prüft ob System production-ready ist.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.agents.core.production_ready import get_checker


if __name__ == "__main__":
    checker = get_checker()
    checker.print_report()
    
    result = checker.run_all_checks()
    sys.exit(0 if result["ready"] else 1)
