"""
Connections Repository

⚠️  WARNING: This is a STUB implementation for development/testing only.
⚠️  DO NOT use this as the source of truth for production connections.

Source of Truth:
- Node-Backend stores Integration/Connection state (via Nango + DB)
- AI-Shield control-plane manages Policies/Presets/Registry only
- Connection state should be read from Node-Backend, not this stub

This repository is:
- In-memory only (not persisted)
- Development/testing skeleton
- NOT suitable for production use

TODO: Remove or replace with read-only adapter that queries Node-Backend.
"""
from typing import Dict, List, Optional
from datetime import datetime, timezone
from .types import Connection, Provider, ConnectionStatus


class ConnectionsRepository:
    """
    In-memory repository für Connections (STUB - development only).
    
    ⚠️  WARNING: This is NOT the source of truth for connections.
    Connection state is managed by Node-Backend (via Nango + DB).
    This stub is for development/testing only.
    """
    
    def __init__(self):
        # In-memory storage: {tenant_id: {provider: Connection}}
        # ⚠️  WARNING: This is NOT persisted and NOT the source of truth
        self._storage: Dict[str, Dict[str, Connection]] = {}
    
    async def get_connection(
        self,
        tenant_id: str,
        provider: Provider
    ) -> Optional[Connection]:
        """Get connection for tenant and provider."""
        tenant_connections = self._storage.get(tenant_id, {})
        return tenant_connections.get(provider.value)
    
    async def list_connections(
        self,
        tenant_id: str
    ) -> List[Connection]:
        """List all connections for a tenant."""
        tenant_connections = self._storage.get(tenant_id, {})
        return list(tenant_connections.values())
    
    async def save_connection(
        self,
        connection: Connection
    ) -> Connection:
        """
        Save or update connection (STUB - development only).
        
        ⚠️  WARNING: This does NOT persist to production storage.
        Connection state should be managed by Node-Backend.
        This method is for development/testing only.
        """
        import warnings
        warnings.warn(
            "ConnectionsRepository.save_connection() is a STUB. "
            "Connection state should be managed by Node-Backend, not AI-Shield control-plane. "
            "This method is for development/testing only.",
            UserWarning,
            stacklevel=2
        )
        
        if connection.tenant_id not in self._storage:
            self._storage[connection.tenant_id] = {}
        
        now = datetime.now(timezone.utc)
        if not connection.created_at:
            connection.created_at = now
        connection.updated_at = now
        
        self._storage[connection.tenant_id][connection.provider.value] = connection
        return connection
    
    async def delete_connection(
        self,
        tenant_id: str,
        provider: Provider
    ) -> bool:
        """Delete connection."""
        tenant_connections = self._storage.get(tenant_id, {})
        if provider.value in tenant_connections:
            del tenant_connections[provider.value]
            return True
        return False
    
    async def update_status(
        self,
        tenant_id: str,
        provider: Provider,
        status: ConnectionStatus,
        nango_connection_id: Optional[str] = None
    ) -> Optional[Connection]:
        """Update connection status."""
        connection = await self.get_connection(tenant_id, provider)
        if not connection:
            return None
        
        connection.status = status
        if nango_connection_id:
            connection.nango_connection_id = nango_connection_id
        connection.updated_at = datetime.now(timezone.utc)
        
        await self.save_connection(connection)
        return connection


# Global repository instance
_connections_repo: Optional[ConnectionsRepository] = None


def get_connections_repo() -> ConnectionsRepository:
    """Get or create global connections repository."""
    global _connections_repo
    if _connections_repo is None:
        _connections_repo = ConnectionsRepository()
    return _connections_repo
