#!/usr/bin/env python3
"""
Test Health Checks - Testet alle Health Checks

Führt Health Checks für alle Agents aus und zeigt Ergebnisse.
"""

import sys
import os

# Füge Projekt-Root zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from apps.agents.core.health_checks import get_health_checker, HealthStatus
from apps.agents.core.agent_registry import get_registry as get_agent_registry


def test_health_checks():
    """Testet alle Health Checks"""
    print("=" * 80)
    print("HEALTH CHECKS TEST")
    print("=" * 80)
    print()
    
    checker = get_health_checker()
    registry = get_agent_registry()
    
    # Overall Health
    print("📊 Overall Health:")
    print("-" * 80)
    overall = checker.get_overall_health()
    print(f"Status: {overall['status']}")
    print(f"Total: {overall['total']}")
    print(f"Healthy: {overall['healthy']} ✅")
    print(f"Degraded: {overall['degraded']} ⚠️")
    print(f"Unhealthy: {overall['unhealthy']} ❌")
    print()
    
    # Alle Agents
    print("🔍 Individual Agent Health:")
    print("-" * 80)
    
    all_checks = checker.check_all_agents()
    
    healthy_count = 0
    degraded_count = 0
    unhealthy_count = 0
    
    for agent_name, result in sorted(all_checks.items()):
        status_icon = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.UNKNOWN: "❓"
        }.get(result.status, "❓")
        
        print(f"{status_icon} {agent_name}")
        print(f"   Status: {result.status.value}")
        print(f"   Message: {result.message}")
        if result.dependencies:
            print(f"   Dependencies: {result.dependencies}")
        if result.response_time_ms:
            print(f"   Response Time: {result.response_time_ms:.2f}ms")
        print()
        
        if result.status == HealthStatus.HEALTHY:
            healthy_count += 1
        elif result.status == HealthStatus.DEGRADED:
            degraded_count += 1
        else:
            unhealthy_count += 1
    
    # Zusammenfassung
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"✅ Healthy: {healthy_count}")
    print(f"⚠️  Degraded: {degraded_count}")
    print(f"❌ Unhealthy: {unhealthy_count}")
    print(f"📊 Total: {len(all_checks)}")
    print()
    
    # Exit Code basierend auf Health
    if unhealthy_count > 0:
        print("❌ FEHLER: Einige Agents sind unhealthy!")
        return 1
    elif degraded_count > 0:
        print("⚠️  WARNUNG: Einige Agents sind degraded!")
        return 0
    else:
        print("✅ ALLE AGENTS SIND HEALTHY!")
        return 0


if __name__ == "__main__":
    exit_code = test_health_checks()
    sys.exit(exit_code)
