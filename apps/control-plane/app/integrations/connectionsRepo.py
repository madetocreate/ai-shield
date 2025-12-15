"""
Connections Repository

In-memory storage für Connections (später DB-basiert).
Aktuell nur Skeleton für Entwicklung.
"""
from typing import Dict, List, Optional
from datetime import datetime, timezone
from .types import Connection, Provider, ConnectionStatus


class ConnectionsRepository:
    """In-memory repository für Connections (später DB)."""
    
    def __init__(self):
        # In-memory storage: {tenant_id: {provider: Connection}}
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
        """Save or update connection."""
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
