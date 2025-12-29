"""
Enhanced Authentication Features
Token Refresh, Logout, Password Reset, Rate Limiting
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
import secrets
import jwt
import os
import hashlib
import logging

from .auth import (
    create_jwt_token,
    verify_jwt_token,
    get_current_user,
    users_db,
    sessions_db,
    password_reset_tokens,
    hash_password,
    verify_password as verify_password_func,
    JWT_EXPIRATION_HOURS,
)

# Logger für Security-Audit-Events
logger = logging.getLogger(__name__)

# Environment Variables
APP_ENV = os.environ.get("APP_ENV", os.environ.get("ENVIRONMENT", "production")).lower()
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")
RESET_TOKEN_SALT = os.environ.get("RESET_TOKEN_SALT", secrets.token_urlsafe(32))
AI_SHIELD_DEV_EXPOSE_RESET_TOKEN = os.environ.get("AI_SHIELD_DEV_EXPOSE_RESET_TOKEN", "false").lower() == "true"

# Enhanced router
enhanced_router = APIRouter(prefix="/v1/auth", tags=["auth"])

# Rate limiting (simple in-memory, use Redis in production)
rate_limit_store: Dict[str, Dict[str, Any]] = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 5


def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers or connection."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip")
    if xri:
        return xri.strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def check_rate_limit(identifier: str, endpoint: str) -> bool:
    """Simple rate limiting."""
    key = f"{identifier}:{endpoint}"
    now = datetime.now(timezone.utc)
    
    if key not in rate_limit_store:
        rate_limit_store[key] = {
            "count": 1,
            "window_start": now,
        }
        return True
    
    store = rate_limit_store[key]
    elapsed = (now - store["window_start"]).total_seconds()
    
    if elapsed > RATE_LIMIT_WINDOW:
        store["count"] = 1
        store["window_start"] = now
        return True
    
    if store["count"] >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    store["count"] += 1
    return True


def hash_reset_token(token: str) -> str:
    """Hash reset token for secure storage (SHA256 with salt)."""
    combined = f"{token}:{RESET_TOKEN_SALT}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def verify_reset_token(token: str, stored_hash: str) -> bool:
    """Verify reset token against stored hash."""
    expected_hash = hash_reset_token(token)
    return secrets.compare_digest(expected_hash, stored_hash)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None


@enhanced_router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(request: RefreshTokenRequest, client_ip: str = Depends(get_client_ip)):
    """Refresh access token using refresh token."""
    if not check_rate_limit(client_ip, "refresh"):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Verify refresh token
    payload = verify_jwt_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if refresh token is in sessions
    if request.refresh_token not in sessions_db:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    # Check if refresh token is expired
    session = sessions_db[request.refresh_token]
    expires_at = datetime.fromisoformat(session["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        # Clean up expired session
        del sessions_db[request.refresh_token]
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Create new access token
    new_access_token = create_jwt_token(user_id, email, refresh=False)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600,
    }


@enhanced_router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Logout user and invalidate refresh tokens."""
    user_id = current_user["id"]
    
    # Remove all refresh tokens for this user
    tokens_to_remove = []
    for token, session in sessions_db.items():
        if session.get("user_id") == user_id:
            tokens_to_remove.append(token)
    
    for token in tokens_to_remove:
        del sessions_db[token]
    
    return {"message": "Logged out successfully"}


@enhanced_router.post("/password/reset/request")
async def request_password_reset(request: PasswordResetRequest, client_ip: str = Depends(get_client_ip)):
    """Request password reset."""
    if not check_rate_limit(client_ip, "password_reset"):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Find user
    user = None
    user_id = None
    for uid, u in users_db.items():
        if u.get("email") == request.email and u.get("provider") == "email":
            user = u
            user_id = uid
            break
    
    # Security: Always return generic message (don't reveal if email exists)
    generic_message = "If the email exists, a password reset link has been sent"
    
    if not user:
        # Log security event (without sensitive data)
        if APP_ENV == "production":
            logger.info(
                "Password reset requested for unknown email",
                extra={
                    "event": "password_reset_requested",
                    "email_exists": False,
                    "client_ip": client_ip,
                }
            )
        return {"message": generic_message}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    token_hash = hash_reset_token(reset_token)
    
    # Store hashed token (not plaintext)
    password_reset_tokens[token_hash] = {
        "user_id": user_id,
        "email": request.email,
        "token_plaintext": reset_token,  # Store plaintext temporarily for lookup (will be removed after use)
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Security: Production mode - never expose token or reset_link in response
    is_production = APP_ENV == "production"
    
    if is_production:
        # Log security audit event (without token)
        logger.info(
            "Password reset token generated",
            extra={
                "event": "password_reset_token_generated",
                "user_id": user_id,
                "email": request.email,
                "client_ip": client_ip,
                "expires_at": password_reset_tokens[token_hash]["expires_at"],
            }
        )
        # In production: Only return generic message
        return {"message": generic_message}
    
    # Development mode: Only expose if explicitly enabled
    if AI_SHIELD_DEV_EXPOSE_RESET_TOKEN:
        reset_link = f"{FRONTEND_BASE_URL}/auth/reset-password?token={reset_token}"
        return {
            "message": "Password reset link sent",
            "reset_link": reset_link,
            "token": reset_token,
        }
    
    # Dev default: Generic message (secure by default)
    return {"message": generic_message}


@enhanced_router.post("/password/reset/confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest, client_ip: str = Depends(get_client_ip)):
    """Confirm password reset with token."""
    if not check_rate_limit(client_ip, "password_reset_confirm"):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Find reset token by hashing the provided token and looking it up
    token_hash = hash_reset_token(request.token)
    
    # Also check plaintext lookup (for backward compatibility during migration)
    reset_data = None
    token_key = None
    
    if token_hash in password_reset_tokens:
        reset_data = password_reset_tokens[token_hash]
        token_key = token_hash
    else:
        # Fallback: Check if token is stored as plaintext (migration period)
        # This allows existing tokens to still work
        for key, data in password_reset_tokens.items():
            if data.get("token_plaintext") == request.token:
                reset_data = data
                token_key = key
                break
    
    if not reset_data or not token_key:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    expires_at = datetime.fromisoformat(reset_data["expires_at"])
    
    if datetime.now(timezone.utc) > expires_at:
        del password_reset_tokens[token_key]
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user_id = reset_data["user_id"]
    if user_id not in users_db:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Update password
    users_db[user_id]["password_hash"] = hash_password(request.new_password)
    
    # Remove reset token
    del password_reset_tokens[token_key]
    
    # Log security event
    if APP_ENV == "production":
        logger.info(
            "Password reset confirmed",
            extra={
                "event": "password_reset_confirmed",
                "user_id": user_id,
                "client_ip": client_ip,
            }
        )
    
    # Invalidate all refresh tokens for security
    tokens_to_remove = []
    for token, session in sessions_db.items():
        if session.get("user_id") == user_id:
            tokens_to_remove.append(token)
    
    for token in tokens_to_remove:
        del sessions_db[token]
    
    return {"message": "Password reset successfully"}


@enhanced_router.post("/password/change")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change password for authenticated user."""
    user_id = current_user["id"]
    user = users_db.get(user_id)
    
    if not user or user.get("provider") != "email":
        raise HTTPException(status_code=400, detail="Password change only available for email accounts")
    
    # Verify current password
    if not verify_password_func(request.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Update password
    users_db[user_id]["password_hash"] = hash_password(request.new_password)
    
    # Invalidate all refresh tokens for security
    tokens_to_remove = []
    for token, session in sessions_db.items():
        if session.get("user_id") == user_id:
            tokens_to_remove.append(token)
    
    for token in tokens_to_remove:
        del sessions_db[token]
    
    return {"message": "Password changed successfully"}


@enhanced_router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile."""
    user_id = current_user["id"]
    user = users_db.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update name if provided
    if request.name is not None:
        users_db[user_id]["name"] = request.name
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": user_id,
            "email": user["email"],
            "name": users_db[user_id]["name"],
            "picture": user.get("picture"),
            "provider": user.get("provider"),
        }
    }


@enhanced_router.delete("/account")
async def delete_account(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete user account."""
    user_id = current_user["id"]
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove user
    del users_db[user_id]
    
    # Remove all sessions
    tokens_to_remove = []
    for token, session in sessions_db.items():
        if session.get("user_id") == user_id:
            tokens_to_remove.append(token)
    
    for token in tokens_to_remove:
        del sessions_db[token]
    
    return {"message": "Account deleted successfully"}


@enhanced_router.get("/sessions")
async def get_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all active sessions for current user."""
    user_id = current_user["id"]
    
    active_sessions = []
    for token, session in sessions_db.items():
        if session.get("user_id") == user_id:
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.now(timezone.utc) < expires_at:
                active_sessions.append({
                    "session_id": token,  # Use token as session_id
                    "created_at": session["created_at"],
                    "expires_at": session["expires_at"],
                    "is_current": False,  # Would need to track current session
                })
    
    return {"sessions": active_sessions}


@enhanced_router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Revoke a specific session."""
    user_id = current_user["id"]
    
    if session_id in sessions_db:
        session = sessions_db[session_id]
        if session.get("user_id") == user_id:
            del sessions_db[session_id]
            return {"message": "Session revoked successfully"}
    
    raise HTTPException(status_code=404, detail="Session not found")
