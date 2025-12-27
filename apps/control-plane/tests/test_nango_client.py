"""
Tests for Nango client.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add control-plane/app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from integrations.nangoClient import NangoClient


@pytest.mark.asyncio
async def test_nango_proxy_headers():
    """Test that proxy() sets Connection-Id and Provider-Config-Key as headers."""
    client = NangoClient(base_url="http://test.nango", api_key="test-key")
    
    # Mock httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_response.raise_for_status = MagicMock()
    
    mock_httpx_client = AsyncMock()
    mock_httpx_client.request = AsyncMock(return_value=mock_response)
    
    # Set client directly to bypass _get_client() which sets Authorization header
    client._client = mock_httpx_client
    
    result = await client.proxy(
        provider_config_key="test-provider",
        connection_id="test-connection-123",
        method="GET",
        endpoint="/api/test",
        params={"foo": "bar"}
    )
    
    # Verify request was called
    assert mock_httpx_client.request.called
    
    # Get call arguments
    call_kwargs = mock_httpx_client.request.call_args[1]
    
    # Verify headers are set correctly
    assert "Connection-Id" in call_kwargs["headers"]
    assert call_kwargs["headers"]["Connection-Id"] == "test-connection-123"
    assert "Provider-Config-Key" in call_kwargs["headers"]
    assert call_kwargs["headers"]["Provider-Config-Key"] == "test-provider"
    
    # Verify endpoint normalization (leading slash removed)
    assert call_kwargs["url"] == "/proxy/api/test"
    
    # Verify params are passed through (not used for Nango params)
    assert call_kwargs["params"] == {"foo": "bar"}


@pytest.mark.asyncio
async def test_nango_get_connection_endpoint():
    """Test that get_connection() uses /connections/{id} endpoint."""
    client = NangoClient(base_url="http://test.nango", api_key="test-key")
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"connection_id": "test-123", "provider": "test-provider"}
    mock_response.raise_for_status = MagicMock()
    
    mock_httpx_client = AsyncMock()
    mock_httpx_client.get = AsyncMock(return_value=mock_response)
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client):
        client._client = mock_httpx_client
        
        result = await client.get_connection(
            connection_id="test-connection-123",
            provider_config_key="test-provider"
        )
        
        # Verify GET was called with correct URL
        assert mock_httpx_client.get.called
        call_args = mock_httpx_client.get.call_args
        
        # Verify endpoint is /connections/{id} (plural)
        assert call_args[0][0] == "/connections/test-connection-123"
        
        # Verify provider_config_key is in params
        assert call_args[1]["params"]["provider_config_key"] == "test-provider"


@pytest.mark.asyncio
async def test_nango_get_access_token_extraction():
    """Test that get_access_token() extracts token from various response formats."""
    client = NangoClient(base_url="http://test.nango", api_key="test-key")
    
    # Test 1: Token in credentials.access_token
    mock_response1 = MagicMock()
    mock_response1.json.return_value = {
        "credentials": {"access_token": "token-from-credentials"}
    }
    mock_response1.raise_for_status = MagicMock()
    
    mock_httpx_client1 = AsyncMock()
    mock_httpx_client1.get = AsyncMock(return_value=mock_response1)
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client1):
        client._client = mock_httpx_client1
        token = await client.get_access_token("test-provider", "test-conn")
        assert token == "token-from-credentials"
    
    # Test 2: Token in credentials.oauth_token
    mock_response2 = MagicMock()
    mock_response2.json.return_value = {
        "credentials": {"oauth_token": "token-from-oauth"}
    }
    mock_response2.raise_for_status = MagicMock()
    
    mock_httpx_client2 = AsyncMock()
    mock_httpx_client2.get = AsyncMock(return_value=mock_response2)
    
    with patch('httpx.AsyncClient', return_value=mock_httpx_client2):
        client._client = mock_httpx_client2
        token = await client.get_access_token("test-provider", "test-conn")
        assert token == "token-from-oauth"

