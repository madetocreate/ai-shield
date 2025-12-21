"""
Apple Sign-In Token Verification mit JWKS

Verifiziert Apple ID Tokens korrekt mit:
- JWKS Fetch von Apple
- Signature Verification
- Issuer Verification (https://appleid.apple.com)
- Audience Verification (APPLE_CLIENT_ID)
- Caching von JWKS Keys (6h TTL)

Was geändert: Neue Implementierung mit korrekter JWKS-basierter Verifikation
Warum: Vorher verify_signature=False - unsicher, ermöglicht Token-Fälschung
Rollback: In auth.py verify_apple_token() wieder zu jwt.decode(..., verify_signature=False) ändern
"""
import os
import json
import jwt
import time
from typing import Dict, Any, Optional
from fastapi import HTTPException
import httpx

APPLE_ISSUER = "https://appleid.apple.com"
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID", "")

# In-memory JWKS cache
_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_cache_time: float = 0
_jwks_cache_ttl: float = 6 * 60 * 60  # 6 hours


async def fetch_apple_jwks() -> Dict[str, Any]:
    """Fetch Apple JWKS with caching (6h TTL)."""
    global _jwks_cache, _jwks_cache_time
    
    # Return cached JWKS if still valid
    if _jwks_cache and (time.time() - _jwks_cache_time) < _jwks_cache_ttl:
        return _jwks_cache
    
    # Fetch fresh JWKS
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(APPLE_JWKS_URL, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = time.time()
            return _jwks_cache
        except Exception as e:
            # If fetch fails but we have cached JWKS, use it
            if _jwks_cache:
                return _jwks_cache
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch Apple JWKS: {str(e)}"
            )


def get_key_from_jwks(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    """Get public key from JWKS by kid (key ID)."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


async def verify_apple_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verify Apple ID token with JWKS signature verification.
    
    Args:
        id_token: Apple ID token string
        
    Returns:
        Dict with sub, email, email_verified, iss, aud
        
    Raises:
        HTTPException: If verification fails
    """
    if not APPLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="APPLE_CLIENT_ID not configured"
        )
    
    try:
        # Decode header to get kid (key ID)
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg", "RS256")
        
        if not kid:
            raise HTTPException(
                status_code=400,
                detail="Apple token missing 'kid' in header"
            )
        
        # Fetch JWKS
        jwks = await fetch_apple_jwks()
        
        # Get public key
        key_data = get_key_from_jwks(jwks, kid)
        if not key_data:
            raise HTTPException(
                status_code=400,
                detail=f"Apple JWKS key not found for kid: {kid}"
            )
        
        # Construct RSA public key from JWK using PyJWT
        # PyJWT's algorithms module has from_jwk method
        # Note: from_jwk expects a dict, not JSON string
        try:
            from jwt.algorithms import RSAAlgorithm
            public_key = RSAAlgorithm.from_jwk(key_data)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to construct public key from JWK: {str(e)}"
            )
        
        # Verify token with signature, issuer, audience
        decoded = jwt.decode(
            id_token,
            public_key,
            algorithms=[alg],  # Typically RS256
            issuer=APPLE_ISSUER,
            audience=APPLE_CLIENT_ID,
            options={
                "verify_signature": True,
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
            }
        )
        
        # Validate required fields
        if not decoded.get("sub"):
            raise HTTPException(
                status_code=400,
                detail="Invalid Apple token: missing 'sub'"
            )
        
        return {
            "sub": decoded.get("sub"),
            "email": decoded.get("email"),
            "email_verified": decoded.get("email_verified", False),
            "iss": decoded.get("iss"),
            "aud": decoded.get("aud"),
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Apple token expired"
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Apple token issuer"
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Apple token audience"
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Apple token signature"
        )
    except jwt.DecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to decode Apple token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Apple token verification failed: {str(e)}"
        )

