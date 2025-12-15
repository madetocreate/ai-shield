#!/usr/bin/env python3
"""
Exportiert Metrics im Prometheus-Format

Kann von Prometheus gescraped werden.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.agents.core.monitoring import get_monitor


if __name__ == "__main__":
    monitor = get_monitor()
    metrics = monitor.export_prometheus_metrics()
    print(metrics)
