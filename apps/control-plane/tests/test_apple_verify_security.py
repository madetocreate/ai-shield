"""
Security tests for apple_verify.py algorithm confusion fix.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from app.apple_verify import verify_apple_id_token


@pytest.mark.asyncio
async def test_reject_non_rs256_algorithm():
    """Test that non-RS256 algorithms are rejected."""
    id_token = "dummy.token.signature"
    
    # Mock unverified header with "none" algorithm (common attack vector)
    with patch('app.apple_verify.jwt.get_unverified_header') as mock_header:
        mock_header.return_value = {"kid": "test-kid", "alg": "none"}
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_apple_id_token(id_token)
        
        assert exc_info.value.status_code == 400
        assert "Invalid Apple token algorithm" in exc_info.value.detail
        assert "none" in exc_info.value.detail


@pytest.mark.asyncio
async def test_reject_hs256_algorithm():
    """Test that HS256 algorithm is rejected (should be RS256)."""
    id_token = "dummy.token.signature"
    
    with patch('app.apple_verify.jwt.get_unverified_header') as mock_header:
        mock_header.return_value = {"kid": "test-kid", "alg": "HS256"}
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_apple_id_token(id_token)
        
        assert exc_info.value.status_code == 400
        assert "Invalid Apple token algorithm" in exc_info.value.detail
        assert "HS256" in exc_info.value.detail


@pytest.mark.asyncio
async def test_accept_rs256_algorithm():
    """Test that RS256 algorithm is accepted."""
    id_token = "dummy.token.signature"
    
    # Mock all dependencies
    with patch('app.apple_verify.jwt.get_unverified_header') as mock_header, \
         patch('app.apple_verify.fetch_apple_jwks') as mock_fetch_jwks, \
         patch('app.apple_verify.get_key_from_jwks') as mock_get_key, \
         patch('app.apple_verify.RSAAlgorithm') as mock_rsa, \
         patch('app.apple_verify.jwt.decode') as mock_decode:
        
        # Setup mocks
        mock_header.return_value = {"kid": "test-kid", "alg": "RS256"}
        mock_fetch_jwks.return_value = {"keys": [{"kid": "test-kid"}]}
        mock_get_key.return_value = {"kty": "RSA", "kid": "test-kid"}
        mock_public_key = Mock()
        mock_rsa.from_jwk.return_value = mock_public_key
        mock_decode.return_value = {
            "sub": "user123",
            "email": "test@example.com",
            "email_verified": True,
            "iss": "https://appleid.apple.com",
            "aud": "test-client-id"
        }
        
        # Mock environment
        with patch.dict('os.environ', {"APPLE_CLIENT_ID": "test-client-id"}):
            result = await verify_apple_id_token(id_token)
            
            # Should succeed
            assert result["sub"] == "user123"
            
            # Verify that decode was called with hardcoded RS256
            mock_decode.assert_called_once()
            call_args = mock_decode.call_args
            assert call_args[1]["algorithms"] == ["RS256"]  # Hardcoded, not from header


@pytest.mark.asyncio
async def test_algorithm_hardcoded_not_from_header():
    """Test that algorithm is hardcoded to RS256, not taken from header."""
    id_token = "dummy.token.signature"
    
    with patch('app.apple_verify.jwt.get_unverified_header') as mock_header, \
         patch('app.apple_verify.fetch_apple_jwks') as mock_fetch_jwks, \
         patch('app.apple_verify.get_key_from_jwks') as mock_get_key, \
         patch('app.apple_verify.RSAAlgorithm') as mock_rsa, \
         patch('app.apple_verify.jwt.decode') as mock_decode:
        
        # Header says RS256 (valid)
        mock_header.return_value = {"kid": "test-kid", "alg": "RS256"}
        mock_fetch_jwks.return_value = {"keys": [{"kid": "test-kid"}]}
        mock_get_key.return_value = {"kty": "RSA", "kid": "test-kid"}
        mock_public_key = Mock()
        mock_rsa.from_jwk.return_value = mock_public_key
        mock_decode.return_value = {
            "sub": "user123",
            "email": "test@example.com",
            "email_verified": True,
            "iss": "https://appleid.apple.com",
            "aud": "test-client-id"
        }
        
        with patch.dict('os.environ', {"APPLE_CLIENT_ID": "test-client-id"}):
            await verify_apple_id_token(id_token)
            
            # Verify decode was called with hardcoded ["RS256"], not with alg from header
            call_kwargs = mock_decode.call_args[1]
            assert call_kwargs["algorithms"] == ["RS256"]
            # Ensure it's a list with only RS256, not dynamically from header
            assert len(call_kwargs["algorithms"]) == 1
            assert call_kwargs["algorithms"][0] == "RS256"

