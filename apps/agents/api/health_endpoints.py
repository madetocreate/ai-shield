"""
Health Check Endpoints - FastAPI Endpoints für Health Checks

Stellt Health Check Endpoints bereit für:
- Orchestrator
- Alle Agents
- Dependencies
- Overall Health
"""

from fastapi import APIRouter, HTTPException
from apps.agents.core.health_checks import get_health_checker
from apps.agents.core.agent_registry import get_registry as get_agent_registry

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def overall_health():
    """
    Overall Health Check
    
    Returns:
        Overall Health Status aller Agents
    """
    checker = get_health_checker()
    return checker.get_overall_health()


@router.get("/agents")
def all_agents_health():
    """
    Health Check für alle Agents
    
    Returns:
        Health Status aller Agents
    """
    checker = get_health_checker()
    results = checker.check_all_agents()
    
    return {
        "agents": {
            name: {
                "status": result.status.value,
                "message": result.message,
                "dependencies": result.dependencies,
                "response_time_ms": result.response_time_ms,
                "last_check": result.last_check.isoformat() if result.last_check else None
            }
            for name, result in results.items()
        }
    }


@router.get("/agents/{agent_name}")
def agent_health(agent_name: str):
    """
    Health Check für spezifischen Agent
    
    Args:
        agent_name: Name des Agents
    
    Returns:
        Health Status des Agents
    """
    checker = get_health_checker()
    result = checker.check_agent(agent_name)
    
    if result.status.value == "unhealthy":
        raise HTTPException(status_code=503, detail=result.message)
    
    return {
        "agent": agent_name,
        "status": result.status.value,
        "message": result.message,
        "dependencies": result.dependencies,
        "response_time_ms": result.response_time_ms,
        "last_check": result.last_check.isoformat() if result.last_check else None
    }


@router.get("/orchestrator")
def orchestrator_health():
    """
    Health Check für Orchestrator
    
    Returns:
        Health Status des Orchestrators
    """
    registry = get_agent_registry()
    
    # Prüfe ob Orchestrator verfügbar ist
    try:
        from apps.agents.core.llm_orchestrator_agent import get_llm_orchestrator
        orchestrator = get_llm_orchestrator()
        
        return {
            "status": "healthy",
            "model": orchestrator.model,
            "tools_count": len(orchestrator.tools),
            "message": "Orchestrator ist verfügbar"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Orchestrator nicht verfügbar: {e}")


@router.get("/dependencies")
def dependencies_health():
    """
    Health Check für Dependencies
    
    Returns:
        Health Status aller Dependencies
    """
    dependencies = {
        "agent_registry": True,
        "mcp_tool_registry": True,
        "monitoring": True,
        "consent_gateway": True,
        "handoff_protocol": True,
    }
    
    # Prüfe jede Dependency
    try:
        from apps.agents.core.agent_registry import get_registry
        get_registry()
    except Exception:
        dependencies["agent_registry"] = False
    
    try:
        from apps.agents.core.mcp_tool_registry import get_mcp_tool_registry
        get_mcp_tool_registry()
    except Exception:
        dependencies["mcp_tool_registry"] = False
    
    try:
        from apps.agents.core.monitoring import get_monitor
        get_monitor()
    except Exception:
        dependencies["monitoring"] = False
    
    all_healthy = all(dependencies.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "dependencies": dependencies
    }
