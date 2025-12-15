"""
Integrations API Endpoints

FastAPI Router für Integrations-Management.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from .types import Provider, Connection, ConnectionStatus, ApprovalRequest
from .connectionsRepo import get_connections_repo
from .policies import get_default_scopes
from .nangoClient import get_nango_client


router = APIRouter(prefix="/v1/integrations", tags=["integrations"])


# Request/Response Models
class ConnectRequest(BaseModel):
    """Request to connect a provider."""
    tenant_id: str = Field(..., description="Tenant/Workspace ID")
    provider: Provider = Field(..., description="Provider name")
    scopes: Optional[List[str]] = Field(None, description="Optional custom scopes (defaults used if not provided)")


class ConnectionResponse(BaseModel):
    """Connection response."""
    tenant_id: str
    provider: str
    status: str
    nango_connection_id: Optional[str] = None
    scopes: List[str]
    auth_url: Optional[str] = None  # OAuth URL for user to visit
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ApprovalRequestResponse(BaseModel):
    """Approval request response."""
    request_id: str
    tenant_id: str
    provider: str
    operation: str
    preview: Optional[dict] = None
    status: str
    created_at: Optional[str] = None


# Helper function to get tenant_id from header (placeholder)
def _get_tenant_id(x_tenant_id: Optional[str] = Header(default=None)) -> str:
    """Get tenant ID from header (placeholder implementation)."""
    if not x_tenant_id:
        # For development: use default tenant
        return "default-tenant"
    return x_tenant_id


@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    x_tenant_id: Optional[str] = Header(default=None),
    x_ai_shield_admin_key: Optional[str] = Header(default=None)
):
    """
    List all connections for a tenant.
    
    Returns list of all provider connections.
    """
    tenant_id = _get_tenant_id(x_tenant_id)
    repo = get_connections_repo()
    connections = await repo.list_connections(tenant_id)
    
    return [
        ConnectionResponse(
            tenant_id=c.tenant_id,
            provider=c.provider.value,
            status=c.status.value,
            nango_connection_id=c.nango_connection_id,
            scopes=c.scopes,
            created_at=c.created_at.isoformat() if c.created_at else None,
            updated_at=c.updated_at.isoformat() if c.updated_at else None
        )
        for c in connections
    ]


@router.post("/{provider}/connect", response_model=ConnectionResponse)
async def connect_provider(
    provider: str,
    request: ConnectRequest,
    x_ai_shield_admin_key: Optional[str] = Header(default=None)
):
    """
    Initiate OAuth connection for a provider.
    
    Returns connection with auth_url for user to visit.
    """
    try:
        provider_enum = Provider(provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    tenant_id = request.tenant_id
    scopes = request.scopes or get_default_scopes(provider_enum)
    
    repo = get_connections_repo()
    
    # Check if connection already exists
    existing = await repo.get_connection(tenant_id, provider_enum)
    if existing and existing.status == ConnectionStatus.CONNECTED:
        raise HTTPException(status_code=400, detail="Provider already connected")
    
    # Create connection record
    connection = Connection(
        tenant_id=tenant_id,
        provider=provider_enum,
        status=ConnectionStatus.PENDING,
        scopes=scopes,
        created_at=datetime.now(timezone.utc)
    )
    
    # TODO: Generate OAuth URL via Nango
    # For now, return stub
    nango = get_nango_client()
    auth_url = None
    
    try:
        # In real implementation:
        # auth_url = await nango.get_auth_url(provider_enum.value, tenant_id, scopes)
        # For now, return placeholder
        auth_url = f"https://nango.example.com/oauth/{provider_enum.value}?tenant={tenant_id}"
    except Exception as e:
        # If Nango not configured, return stub URL
        auth_url = f"http://localhost:3003/oauth/{provider_enum.value}?tenant={tenant_id}&scopes={','.join(scopes)}"
    
    connection = await repo.save_connection(connection)
    
    return ConnectionResponse(
        tenant_id=connection.tenant_id,
        provider=connection.provider.value,
        status=connection.status.value,
        nango_connection_id=connection.nango_connection_id,
        scopes=connection.scopes,
        auth_url=auth_url,
        created_at=connection.created_at.isoformat() if connection.created_at else None,
        updated_at=connection.updated_at.isoformat() if connection.updated_at else None
    )


@router.post("/{provider}/disconnect")
async def disconnect_provider(
    provider: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    x_ai_shield_admin_key: Optional[str] = Header(default=None)
):
    """
    Disconnect a provider.
    
    Removes connection and revokes access.
    """
    try:
        provider_enum = Provider(provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    repo = get_connections_repo()
    connection = await repo.get_connection(tenant_id, provider_enum)
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # TODO: Revoke access via Nango
    # For now, just delete from repo
    await repo.delete_connection(tenant_id, provider_enum)
    
    return {"ok": True, "message": f"{provider} disconnected"}


@router.get("/{provider}/status", response_model=ConnectionResponse)
async def get_connection_status(
    provider: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    x_ai_shield_admin_key: Optional[str] = Header(default=None)
):
    """
    Get connection status for a provider.
    """
    try:
        provider_enum = Provider(provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    repo = get_connections_repo()
    connection = await repo.get_connection(tenant_id, provider_enum)
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return ConnectionResponse(
        tenant_id=connection.tenant_id,
        provider=connection.provider.value,
        status=connection.status.value,
        nango_connection_id=connection.nango_connection_id,
        scopes=connection.scopes,
        created_at=connection.created_at.isoformat() if connection.created_at else None,
        updated_at=connection.updated_at.isoformat() if connection.updated_at else None
    )


@router.post("/{provider}/callback")
async def oauth_callback(
    provider: str,
    connection_id: str = Query(..., description="Nango connection ID"),
    tenant_id: str = Query(..., description="Tenant ID"),
    x_ai_shield_admin_key: Optional[str] = Header(default=None)
):
    """
    OAuth callback endpoint (called by Nango after successful auth).
    
    Updates connection status to connected.
    """
    try:
        provider_enum = Provider(provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    repo = get_connections_repo()
    connection = await repo.get_connection(tenant_id, provider_enum)
    
    if not connection:
        # Create new connection if doesn't exist
        connection = Connection(
            tenant_id=tenant_id,
            provider=provider_enum,
            status=ConnectionStatus.PENDING,
            nango_connection_id=connection_id,
            created_at=datetime.now(timezone.utc)
        )
    
    # Update connection
    connection.nango_connection_id = connection_id
    connection.status = ConnectionStatus.CONNECTED
    connection.updated_at = datetime.now(timezone.utc)
    
    await repo.save_connection(connection)
    
    return {
        "ok": True,
        "message": f"{provider} connected successfully",
        "connection_id": connection_id
    }
