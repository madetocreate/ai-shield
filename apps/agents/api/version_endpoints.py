"""
Version API Endpoints - FastAPI Endpoints für Agent Versioning

Endpoints:
- GET /api/v1/versions/agents/{agent_name} - Version History
- POST /api/v1/versions/agents/{agent_name} - Neue Version erstellen
- PUT /api/v1/versions/agents/{agent_name}/activate - Version aktivieren
- POST /api/v1/versions/agents/{agent_name}/rollback - Rollback
- GET /api/v1/versions/agents/{agent_name}/compare - Versionen vergleichen
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from apps.agents.core.agent_versioning import (
    get_version_manager,
    VersionType
)

router = APIRouter(prefix="/api/v1/versions", tags=["versions"])


# Request Models
class CreateVersionRequest(BaseModel):
    code: str
    description: str
    version_type: str = "patch"  # major, minor, patch
    changelog: List[str] = []
    dependencies: Dict[str, str] = {}
    created_by: Optional[str] = None


# Response Models
class VersionResponse(BaseModel):
    agent_name: str
    version: str
    version_type: str
    description: str
    changelog: List[str]
    dependencies: Dict[str, str]
    created_at: str
    created_by: Optional[str]
    is_active: bool


@router.get("/agents/{agent_name}", response_model=List[VersionResponse])
def get_version_history(agent_name: str):
    """Holt Version History für Agent"""
    manager = get_version_manager()
    history = manager.get_version_history(agent_name)
    
    if not history:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    
    return [
        VersionResponse(
            agent_name=v.agent_name,
            version=v.version,
            version_type=v.version_type.value,
            description=v.description,
            changelog=v.changelog,
            dependencies=v.dependencies,
            created_at=v.created_at.isoformat(),
            created_by=v.created_by,
            is_active=v.is_active
        )
        for v in history
    ]


@router.get("/agents/{agent_name}/active", response_model=VersionResponse)
def get_active_version(agent_name: str):
    """Holt aktive Version"""
    manager = get_version_manager()
    version = manager.get_active_version(agent_name)
    
    if not version:
        raise HTTPException(status_code=404, detail="Keine aktive Version gefunden")
    
    return VersionResponse(
        agent_name=version.agent_name,
        version=version.version,
        version_type=version.version_type.value,
        description=version.description,
        changelog=version.changelog,
        dependencies=version.dependencies,
        created_at=version.created_at.isoformat(),
        created_by=version.created_by,
        is_active=version.is_active
    )


@router.post("/agents/{agent_name}", response_model=VersionResponse)
def create_version(agent_name: str, request: CreateVersionRequest):
    """Erstellt neue Version"""
    manager = get_version_manager()
    
    try:
        version_type = VersionType(request.version_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Version Type: {request.version_type}")
    
    version = manager.create_version(
        agent_name=agent_name,
        code=request.code,
        description=request.description,
        version_type=version_type,
        changelog=request.changelog,
        dependencies=request.dependencies,
        created_by=request.created_by
    )
    
    return VersionResponse(
        agent_name=version.agent_name,
        version=version.version,
        version_type=version.version_type.value,
        description=version.description,
        changelog=version.changelog,
        dependencies=version.dependencies,
        created_at=version.created_at.isoformat(),
        created_by=version.created_by,
        is_active=version.is_active
    )


@router.put("/agents/{agent_name}/activate")
def activate_version(agent_name: str, version: str = Body(..., embed=True)):
    """Aktiviert Version"""
    manager = get_version_manager()
    success = manager.activate_version(agent_name, version)
    
    if not success:
        raise HTTPException(status_code=404, detail="Version nicht gefunden")
    
    return {"success": True, "message": f"Version {version} aktiviert"}


@router.post("/agents/{agent_name}/rollback")
def rollback_version(
    agent_name: str,
    target_version: Optional[str] = Body(None, embed=True)
):
    """Rollback zu älterer Version"""
    manager = get_version_manager()
    success = manager.rollback(agent_name, target_version)
    
    if not success:
        raise HTTPException(status_code=404, detail="Rollback fehlgeschlagen")
    
    return {"success": True, "message": f"Rollback zu Version {target_version or 'previous'}"}


@router.get("/agents/{agent_name}/compare")
def compare_versions(
    agent_name: str,
    version1: str,
    version2: str
):
    """Vergleicht zwei Versionen"""
    manager = get_version_manager()
    comparison = manager.compare_versions(agent_name, version1, version2)
    
    if "error" in comparison:
        raise HTTPException(status_code=404, detail=comparison["error"])
    
    return comparison
