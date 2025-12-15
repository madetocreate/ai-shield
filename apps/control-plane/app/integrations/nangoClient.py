"""
Nango HTTP Client Wrapper

Wrapper für Nango API Calls. Aktuell nur Skeleton, später mit echten Credentials.
"""
import os
from typing import Any, Dict, Optional
import httpx


NANGO_BASE_URL = os.environ.get("NANGO_BASE_URL", "http://127.0.0.1:3003").rstrip("/")
NANGO_API_KEY = os.environ.get("NANGO_API_KEY", "")


class NangoClient:
    """HTTP Client für Nango API."""
    
    def __init__(self, base_url: str = NANGO_BASE_URL, api_key: str = NANGO_API_KEY):
        self.base_url = base_url
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0
            )
        return self._client
    
    async def get_connection(
        self,
        provider: str,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Get connection details from Nango.
        
        Returns connection info or raises exception if not found.
        """
        if not self.api_key:
            raise ValueError("NANGO_API_KEY not configured")
        
        client = await self._get_client()
        url = f"/connection/{connection_id}"
        params = {"provider_config_key": provider}
        
        response = await client.get(url, params=params)
        if response.status_code == 404:
            raise ValueError(f"Connection {connection_id} not found for provider {provider}")
        response.raise_for_status()
        return response.json()
    
    async def get_access_token(
        self,
        provider: str,
        connection_id: str
    ) -> str:
        """
        Get access token for a connection.
        
        Returns access token string.
        """
        if not self.api_key:
            raise ValueError("NANGO_API_KEY not configured")
        
        client = await self._get_client()
        url = f"/connection/{connection_id}"
        params = {"provider_config_key": provider}
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("credentials", {}).get("access_token", "")
    
    async def proxy(
        self,
        provider: str,
        connection_id: str,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Proxy request to provider API via Nango.
        
        Args:
            provider: Provider config key
            connection_id: Connection ID
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to provider base)
            params: Query parameters
            json_data: JSON body for POST/PUT requests
        
        Returns:
            Response JSON
        """
        if not self.api_key:
            raise ValueError("NANGO_API_KEY not configured")
        
        client = await self._get_client()
        url = f"/proxy/{endpoint}"
        params_dict = params or {}
        params_dict["provider_config_key"] = provider
        params_dict["connection_id"] = connection_id
        
        response = await client.request(
            method=method,
            url=url,
            params=params_dict,
            json=json_data
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Global client instance
_nango_client: Optional[NangoClient] = None


def get_nango_client() -> NangoClient:
    """Get or create global Nango client instance."""
    global _nango_client
    if _nango_client is None:
        _nango_client = NangoClient()
    return _nango_client
