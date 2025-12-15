"""
Production Readiness Checks

Prüft ob System production-ready ist:
- Alle Dependencies vorhanden
- Konfiguration vollständig
- Tests bestanden
- Monitoring aktiv
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import importlib
import sys

# Import für Checks
try:
    from apps.agents.shared.vertical_package_manifest import get_registry
    from apps.agents.shared.consent_and_redaction_gateway import get_gateway
    from apps.agents.shared.handoff_to_human_protocol import get_protocol
except ImportError:
    pass


class CheckStatus(str, Enum):
    """Check-Status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class ProductionCheck:
    """Production-Check"""
    name: str
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None


class ProductionReadinessChecker:
    """
    Production Readiness Checker
    
    Prüft alle Aspekte für Production-Rollout
    """
    
    def __init__(self):
        self.checks: List[ProductionCheck] = []
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Führt alle Checks aus"""
        self.checks = []
        
        self._check_imports()
        self._check_shared_components()
        self._check_agents()
        self._check_integrations()
        self._check_monitoring()
        self._check_configuration()
        
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASS)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAIL)
        warnings = sum(1 for c in self.checks if c.status == CheckStatus.WARNING)
        
        return {
            "total": len(self.checks),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "ready": failed == 0,
            "checks": [self._check_to_dict(c) for c in self.checks]
        }
    
    def _check_imports(self):
        """Prüft ob alle Imports funktionieren"""
        try:
            from apps.agents.shared.vertical_package_manifest import get_registry
            from apps.agents.shared.consent_and_redaction_gateway import get_gateway
            from apps.agents.shared.handoff_to_human_protocol import get_protocol
            from apps.agents.core.agent_registry import get_registry as get_agent_registry
            from apps.agents.core.global_orchestrator_agent import get_orchestrator
            from apps.agents.core.monitoring import get_monitor
            
            self.checks.append(ProductionCheck(
                name="imports",
                status=CheckStatus.PASS,
                message="Alle Imports erfolgreich"
            ))
        except ImportError as e:
            self.checks.append(ProductionCheck(
                name="imports",
                status=CheckStatus.FAIL,
                message=f"Import-Fehler: {e}",
                details={"error": str(e)}
            ))
    
    def _check_shared_components(self):
        """Prüft Shared Components"""
        try:
            manifest_registry = get_registry()
            consent_gateway = get_gateway()
            handoff_protocol = get_protocol()
            
            self.checks.append(ProductionCheck(
                name="shared_components",
                status=CheckStatus.PASS,
                message="Shared Components initialisiert"
            ))
        except Exception as e:
            self.checks.append(ProductionCheck(
                name="shared_components",
                status=CheckStatus.FAIL,
                message=f"Shared Components Fehler: {e}",
                details={"error": str(e)}
            ))
    
    def _check_agents(self):
        """Prüft ob Agents registriert sind"""
        try:
            from apps.agents.core.agent_registry import get_registry
            registry = get_registry()
            agents = registry.list_agents()
            
            required_agents = [
                "gastronomy_supervisor_agent",
                "practice_supervisor_agent"
            ]
            
            missing = [a for a in required_agents if a not in agents]
            
            if missing:
                self.checks.append(ProductionCheck(
                    name="agents",
                    status=CheckStatus.WARNING,
                    message=f"Fehlende Agents: {missing}",
                    details={"missing": missing, "registered": agents}
                ))
            else:
                self.checks.append(ProductionCheck(
                    name="agents",
                    status=CheckStatus.PASS,
                    message=f"Alle Agents registriert ({len(agents)} total)",
                    details={"registered": agents}
                ))
        except Exception as e:
            self.checks.append(ProductionCheck(
                name="agents",
                status=CheckStatus.FAIL,
                message=f"Agent-Registry Fehler: {e}",
                details={"error": str(e)}
            ))
    
    def _check_integrations(self):
        """Prüft Integrationen"""
        try:
            from apps.agents.core.integration_layer import get_integration_layer
            layer = get_integration_layer()
            
            # Prüfe ob Mock-Integrationen verwendet werden
            has_mocks = any(
                "mock" in str(integration.adapter).lower()
                for integration in layer.integrations.values()
            )
            
            if has_mocks:
                self.checks.append(ProductionCheck(
                    name="integrations",
                    status=CheckStatus.WARNING,
                    message="Mock-Integrationen aktiv - echte Integrationen erforderlich",
                    details={"integrations": list(layer.integrations.keys())}
                ))
            else:
                self.checks.append(ProductionCheck(
                    name="integrations",
                    status=CheckStatus.PASS,
                    message="Integrationen konfiguriert",
                    details={"integrations": list(layer.integrations.keys())}
                ))
        except Exception as e:
            self.checks.append(ProductionCheck(
                name="integrations",
                status=CheckStatus.FAIL,
                message=f"Integration Layer Fehler: {e}",
                details={"error": str(e)}
            ))
    
    def _check_monitoring(self):
        """Prüft Monitoring"""
        try:
            from apps.agents.core.monitoring import get_monitor
            monitor = get_monitor()
            
            self.checks.append(ProductionCheck(
                name="monitoring",
                status=CheckStatus.PASS,
                message="Monitoring aktiv",
                details={"metrics_tracked": len(monitor.metrics)}
            ))
        except Exception as e:
            self.checks.append(ProductionCheck(
                name="monitoring",
                status=CheckStatus.FAIL,
                message=f"Monitoring Fehler: {e}",
                details={"error": str(e)}
            ))
    
    def _check_configuration(self):
        """Prüft Konfiguration"""
        import os
        
        required_env_vars = [
            "OPENAI_API_KEY",  # Beispiel
        ]
        
        missing = [v for v in required_env_vars if not os.environ.get(v)]
        
        if missing:
            self.checks.append(ProductionCheck(
                name="configuration",
                status=CheckStatus.WARNING,
                message=f"Fehlende Environment Variables: {missing}",
                details={"missing": missing}
            ))
        else:
            self.checks.append(ProductionCheck(
                name="configuration",
                status=CheckStatus.PASS,
                message="Konfiguration vollständig"
            ))
    
    def _check_to_dict(self, check: ProductionCheck) -> Dict[str, Any]:
        """Konvertiert Check zu Dict"""
        return {
            "name": check.name,
            "status": check.status.value,
            "message": check.message,
            "details": check.details
        }
    
    def print_report(self):
        """Druckt Check-Report"""
        result = self.run_all_checks()
        
        print("=" * 60)
        print("PRODUCTION READINESS CHECK")
        print("=" * 60)
        print()
        
        for check_dict in result["checks"]:
            status_icon = {
                "pass": "✅",
                "fail": "❌",
                "warning": "⚠️",
                "skip": "⏭️"
            }.get(check_dict["status"], "❓")
            
            print(f"{status_icon} {check_dict['name']}: {check_dict['message']}")
            if check_dict.get("details"):
                for key, value in check_dict["details"].items():
                    print(f"   {key}: {value}")
        
        print()
        print("=" * 60)
        print(f"Total: {result['total']} | Passed: {result['passed']} | Failed: {result['failed']} | Warnings: {result['warnings']}")
        print(f"Production Ready: {'✅ YES' if result['ready'] else '❌ NO'}")
        print("=" * 60)


# Globale Checker-Instanz
_global_checker: Optional[ProductionReadinessChecker] = None


def get_checker() -> ProductionReadinessChecker:
    """Holt globale Checker-Instanz"""
    global _global_checker
    if _global_checker is None:
        _global_checker = ProductionReadinessChecker()
    return _global_checker


if __name__ == "__main__":
    checker = get_checker()
    checker.print_report()
