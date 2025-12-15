"""
Health Checks - Health Check Endpoints für alle Agents

Prüft:
- Agent-Verfügbarkeit
- Dependencies
- Performance
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from apps.agents.core.agent_registry import get_registry as get_agent_registry
from apps.agents.core.mcp_tool_registry import get_mcp_tool_registry


class HealthStatus(str, Enum):
    """Health Status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health Check Ergebnis"""
    agent_name: str
    status: HealthStatus
    message: str
    dependencies: Dict[str, bool] = None
    response_time_ms: Optional[float] = None
    last_check: datetime = None
    details: Dict[str, Any] = None


class HealthChecker:
    """
    Health Checker für Agents
    
    Prüft Verfügbarkeit, Dependencies, Performance.
    """
    
    def __init__(self):
        self.agent_registry = get_agent_registry()
        self.mcp_registry = get_mcp_tool_registry()
        self.health_cache: Dict[str, HealthCheckResult] = {}
    
    def check_agent(
        self,
        agent_name: str,
        account_id: str = "test"
    ) -> HealthCheckResult:
        """
        Prüft Health eines Agents
        
        Returns:
            HealthCheckResult
        """
        start_time = time.time()
        
        # Prüfe ob Agent registriert ist
        if not self.agent_registry.is_registered(agent_name):
            return HealthCheckResult(
                agent_name=agent_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Agent {agent_name} nicht registriert",
                last_check=datetime.now()
            )
        
        # Prüfe ob Agent aktiviert ist
        if not self.agent_registry.is_enabled(agent_name):
            return HealthCheckResult(
                agent_name=agent_name,
                status=HealthStatus.DEGRADED,
                message=f"Agent {agent_name} deaktiviert",
                last_check=datetime.now()
            )
        
        # Versuche Agent zu instanziieren
        try:
            agent = self.agent_registry.get_agent(agent_name, account_id)
            if not agent:
                return HealthCheckResult(
                    agent_name=agent_name,
                    status=HealthStatus.DEGRADED,
                    message=f"Agent {agent_name} konnte nicht instanziiert werden",
                    last_check=datetime.now()
                )
        except Exception as e:
            return HealthCheckResult(
                agent_name=agent_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Fehler bei Instanziierung: {e}",
                last_check=datetime.now()
            )
        
        # Prüfe Dependencies
        dependencies = self._check_dependencies(agent_name)
        
        # Prüfe MCP Tool
        mcp_tool = self.mcp_registry.get_tool_by_agent_name(agent_name)
        mcp_available = mcp_tool is not None
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        # Status bestimmen
        if all(dependencies.values()) and mcp_available:
            status = HealthStatus.HEALTHY
            message = "Agent ist gesund"
        elif any(dependencies.values()):
            status = HealthStatus.DEGRADED
            message = "Agent ist verfügbar, aber einige Dependencies fehlen"
        else:
            status = HealthStatus.UNHEALTHY
            message = "Agent ist nicht verfügbar"
        
        result = HealthCheckResult(
            agent_name=agent_name,
            status=status,
            message=message,
            dependencies={**dependencies, "mcp_tool": mcp_available},
            response_time_ms=response_time,
            last_check=datetime.now()
        )
        
        self.health_cache[agent_name] = result
        return result
    
    def _check_dependencies(self, agent_name: str) -> Dict[str, bool]:
        """Prüft Dependencies eines Agents"""
        config = self.agent_registry._agents.get(agent_name)
        if not config or not config.dependencies:
            return {}
        
        dependencies = {}
        for dep_name, dep_agent_name in config.dependencies.items():
            dependencies[dep_name] = self.agent_registry.is_registered(dep_agent_name)
        
        return dependencies
    
    def check_all_agents(self) -> Dict[str, HealthCheckResult]:
        """Prüft Health aller Agents"""
        results = {}
        
        for agent_name in self.agent_registry.list_agents():
            results[agent_name] = self.check_agent(agent_name)
        
        return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Holt Overall Health Status"""
        all_checks = self.check_all_agents()
        
        healthy = sum(1 for r in all_checks.values() if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in all_checks.values() if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in all_checks.values() if r.status == HealthStatus.UNHEALTHY)
        total = len(all_checks)
        
        overall_status = HealthStatus.HEALTHY
        if unhealthy > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "total": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "checks": {name: {
                "status": result.status.value,
                "message": result.message,
                "response_time_ms": result.response_time_ms
            } for name, result in all_checks.items()}
        }


# Globale Health Checker-Instanz
_global_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Holt globale Health Checker-Instanz"""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker


# Import für time
import time
