"""
Marketplace API Endpoints - FastAPI Endpoints für App Marketplace

Endpoints:
- GET /api/v1/marketplace/agents - Suche Agents
- GET /api/v1/marketplace/agents/{agent_id} - Agent Details
- POST /api/v1/marketplace/agents - Agent veröffentlichen
- POST /api/v1/marketplace/agents/{agent_id}/rate - Agent bewerten
- POST /api/v1/marketplace/agents/{agent_id}/install - Agent installieren
- DELETE /api/v1/marketplace/agents/{agent_id}/install - Agent deinstallieren
- GET /api/v1/marketplace/installed - Installierte Agents
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List
from pydantic import BaseModel
from apps.agents.core.app_marketplace import (
    get_marketplace,
    MarketplaceAgent,
    AgentCategory,
    AgentStatus
)

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


# Request Models
class PublishAgentRequest(BaseModel):
    id: str
    name: str
    description: str
    author: str
    version: str
    category: str
    tags: List[str] = []
    dependencies: List[str] = []
    code_url: Optional[str] = None
    documentation_url: Optional[str] = None
    license: Optional[str] = None
    metadata: dict = {}


class RateAgentRequest(BaseModel):
    user_id: str
    rating: int  # 1-5
    comment: Optional[str] = None


# Response Models
class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    author: str
    version: str
    category: str
    status: str
    tags: List[str]
    dependencies: List[str]
    installation_count: int
    average_rating: float
    rating_count: int
    created_at: str
    updated_at: str
    code_url: Optional[str] = None
    documentation_url: Optional[str] = None
    license: Optional[str] = None


@router.get("/agents", response_model=List[AgentResponse])
def search_agents(
    query: Optional[str] = Query(None, description="Suchanfrage"),
    category: Optional[str] = Query(None, description="Kategorie"),
    tags: Optional[str] = Query(None, description="Tags (comma-separated)"),
    min_rating: Optional[float] = Query(None, description="Mindest-Rating"),
    limit: int = Query(20, description="Maximale Anzahl Ergebnisse")
):
    """
    Sucht Agents im Marketplace
    """
    marketplace = get_marketplace()
    
    category_enum = None
    if category:
        try:
            category_enum = AgentCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültige Kategorie: {category}")
    
    tags_list = tags.split(",") if tags else None
    
    results = marketplace.search_agents(
        query=query,
        category=category_enum,
        tags=tags_list,
        min_rating=min_rating,
        limit=limit
    )
    
    return [
        AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            author=agent.author,
            version=agent.version,
            category=agent.category.value,
            status=agent.status.value,
            tags=agent.tags,
            dependencies=agent.dependencies,
            installation_count=agent.installation_count,
            average_rating=agent.average_rating,
            rating_count=agent.rating_count,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat(),
            code_url=agent.code_url,
            documentation_url=agent.documentation_url,
            license=agent.license
        )
        for agent in results
    ]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str):
    """
    Holt Agent Details
    """
    marketplace = get_marketplace()
    
    if agent_id not in marketplace.agents:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    
    agent = marketplace.agents[agent_id]
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        author=agent.author,
        version=agent.version,
        category=agent.category.value,
        status=agent.status.value,
        tags=agent.tags,
        dependencies=agent.dependencies,
        installation_count=agent.installation_count,
        average_rating=agent.average_rating,
        rating_count=agent.rating_count,
        created_at=agent.created_at.isoformat(),
        updated_at=agent.updated_at.isoformat(),
        code_url=agent.code_url,
        documentation_url=agent.documentation_url,
        license=agent.license
    )


@router.post("/agents", response_model=AgentResponse)
def publish_agent(request: PublishAgentRequest):
    """
    Veröffentlicht Agent im Marketplace
    """
    marketplace = get_marketplace()
    
    try:
        category = AgentCategory(request.category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Kategorie: {request.category}")
    
    agent = MarketplaceAgent(
        id=request.id,
        name=request.name,
        description=request.description,
        author=request.author,
        version=request.version,
        category=category,
        status=AgentStatus.PUBLISHED,
        tags=request.tags,
        dependencies=request.dependencies,
        code_url=request.code_url,
        documentation_url=request.documentation_url,
        license=request.license,
        metadata=request.metadata
    )
    
    success = marketplace.publish_agent(agent)
    if not success:
        raise HTTPException(status_code=500, detail="Fehler beim Veröffentlichen")
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        author=agent.author,
        version=agent.version,
        category=agent.category.value,
        status=agent.status.value,
        tags=agent.tags,
        dependencies=agent.dependencies,
        installation_count=agent.installation_count,
        average_rating=agent.average_rating,
        rating_count=agent.rating_count,
        created_at=agent.created_at.isoformat(),
        updated_at=agent.updated_at.isoformat(),
        code_url=agent.code_url,
        documentation_url=agent.documentation_url,
        license=agent.license
    )


@router.post("/agents/{agent_id}/rate")
def rate_agent(agent_id: str, request: RateAgentRequest):
    """
    Bewertet Agent
    """
    marketplace = get_marketplace()
    
    if agent_id not in marketplace.agents:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating muss zwischen 1 und 5 sein")
    
    success = marketplace.rate_agent(
        agent_id=agent_id,
        user_id=request.user_id,
        rating=request.rating,
        comment=request.comment
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Fehler beim Bewerten")
    
    return {"success": True, "message": "Rating hinzugefügt"}


@router.post("/agents/{agent_id}/install")
def install_agent(agent_id: str, account_id: str = Body(..., embed=True)):
    """
    Installiert Agent für Account
    """
    marketplace = get_marketplace()
    
    if agent_id not in marketplace.agents:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    
    success = marketplace.install_agent(agent_id, account_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Fehler beim Installieren")
    
    return {"success": True, "message": "Agent installiert"}


@router.delete("/agents/{agent_id}/install")
def uninstall_agent(agent_id: str, account_id: str = Body(..., embed=True)):
    """
    Deinstalliert Agent für Account
    """
    marketplace = get_marketplace()
    
    success = marketplace.uninstall_agent(agent_id, account_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Agent nicht installiert")
    
    return {"success": True, "message": "Agent deinstalliert"}


@router.get("/installed/{account_id}", response_model=List[AgentResponse])
def get_installed_agents(account_id: str):
    """
    Holt installierte Agents für Account
    """
    marketplace = get_marketplace()
    installed = marketplace.get_installed_agents(account_id)
    
    return [
        AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            author=agent.author,
            version=agent.version,
            category=agent.category.value,
            status=agent.status.value,
            tags=agent.tags,
            dependencies=agent.dependencies,
            installation_count=agent.installation_count,
            average_rating=agent.average_rating,
            rating_count=agent.rating_count,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat(),
            code_url=agent.code_url,
            documentation_url=agent.documentation_url,
            license=agent.license
        )
        for agent in installed
    ]
