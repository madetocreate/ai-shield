"""
Nango HTTP Client Wrapper

Wrapper für Nango API Calls. Aktuell nur Skeleton, später mit echten Credentials.

ENV Variables (canonical):
- NANGO_HOST: Nango instance URL (canonical)
- NANGO_SECRET_KEY: Nango secret key (canonical)

Deprecated (backward compatibility):
- NANGO_BASE_URL: Alias for NANGO_HOST (with deprecation warning)
- NANGO_API_KEY: Alias for NANGO_SECRET_KEY (with deprecation warning)
"""
import os
import warnings
from typing import Any, Dict, Optional
import httpx

# Canonical ENV names (preferred)
NANGO_HOST = os.environ.get("NANGO_HOST", "").rstrip("/")
NANGO_SECRET_KEY = os.environ.get("NANGO_SECRET_KEY", "")

# Deprecated ENV names (backward compatibility with warning)
NANGO_BASE_URL = os.environ.get("NANGO_BASE_URL", "").rstrip("/")
NANGO_API_KEY = os.environ.get("NANGO_API_KEY", "")

# Use canonical names, fallback to deprecated with warning
if not NANGO_HOST and NANGO_BASE_URL:
    warnings.warn(
        "NANGO_BASE_URL is deprecated. Please use NANGO_HOST instead. "
        "NANGO_BASE_URL will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    NANGO_HOST = NANGO_BASE_URL

if not NANGO_SECRET_KEY and NANGO_API_KEY:
    warnings.warn(
        "NANGO_API_KEY is deprecated. Please use NANGO_SECRET_KEY instead. "
        "NANGO_API_KEY will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    NANGO_SECRET_KEY = NANGO_API_KEY

# Default fallback for development
if not NANGO_HOST:
    NANGO_HOST = "http://127.0.0.1:3003"


class NangoClient:
    """HTTP Client für Nango API."""
    
    def __init__(self, base_url: str = NANGO_HOST, api_key: str = NANGO_SECRET_KEY):
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
        connection_id: str,
        provider_config_key: str
    ) -> Dict[str, Any]:
        """
        Get connection details from Nango.
        
        Args:
            connection_id: Connection ID
            provider_config_key: Provider config key
        
        Returns connection info or raises exception if not found.
        """
        if not self.api_key:
            raise ValueError("NANGO_SECRET_KEY (or deprecated NANGO_API_KEY) not configured")
        
        client = await self._get_client()
        # Use plural endpoint: /connections/{connection_id}
        url = f"/connections/{connection_id}"
        params = {"provider_config_key": provider_config_key}
        
        response = await client.get(url, params=params)
        if response.status_code == 404:
            raise ValueError(f"Connection {connection_id} not found for provider {provider_config_key}")
        response.raise_for_status()
        return response.json()
    
    async def get_access_token(
        self,
        provider: str,
        connection_id: str
    ) -> str:
        """
        Get access token for a connection.
        
        Args:
            provider: Provider config key
            connection_id: Connection ID
        
        Returns access token string.
        """
        if not self.api_key:
            raise ValueError("NANGO_SECRET_KEY (or deprecated NANGO_API_KEY) not configured")
        
        client = await self._get_client()
        # Use plural endpoint: /connections/{connection_id}
        url = f"/connections/{connection_id}"
        params = {"provider_config_key": provider}
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Try multiple possible token fields (Nango API may vary)
        credentials = data.get("credentials", {})
        access_token = (
            credentials.get("access_token") or
            credentials.get("oauth_token") or
            data.get("access_token") or
            data.get("oauth_token") or
            ""
        )
        
        if not access_token:
            raise ValueError(f"No access token found in response for connection {connection_id}")
        
        return access_token
    
    async def proxy(
        self,
        provider_config_key: str,
        connection_id: str,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Proxy request to provider API via Nango.
        
        Args:
            provider_config_key: Provider config key
            connection_id: Connection ID
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to provider base, will be normalized)
            params: Query parameters for downstream API (not Nango params)
            json_data: JSON body for POST/PUT requests
            data: Form data (alternative to json_data)
            headers: Additional headers (Connection-Id and Provider-Config-Key are set automatically)
        
        Returns:
            Response JSON
        """
        if not self.api_key:
            raise ValueError("NANGO_SECRET_KEY (or deprecated NANGO_API_KEY) not configured")
        
        client = await self._get_client()
        
        # Normalize endpoint: remove leading slash
        endpoint_normalized = endpoint.lstrip("/")
        url = f"/proxy/{endpoint_normalized}"
        
        # Set required headers (Nango proxy requires these as headers, not query params)
        request_headers = headers.copy() if headers else {}
        request_headers["Connection-Id"] = connection_id
        request_headers["Provider-Config-Key"] = provider_config_key
        
        # Use params only for downstream query params (not Nango params)
        response = await client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            data=data,
            headers=request_headers
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
