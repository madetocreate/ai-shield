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

# Enhanced router
enhanced_router = APIRouter(prefix="/v1/auth", tags=["auth"])

# Rate limiting (simple in-memory, use Redis in production)
rate_limit_store: Dict[str, Dict[str, Any]] = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 5


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
async def refresh_token(request: RefreshTokenRequest, client_ip: str = Depends(lambda: "unknown")):
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
async def request_password_reset(request: PasswordResetRequest, client_ip: str = Depends(lambda: "unknown")):
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
    
    if not user:
        # Don't reveal if email exists (security best practice)
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    password_reset_tokens[reset_token] = {
        "user_id": user_id,
        "email": request.email,
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # In production, send email with reset link
    # For now, we'll just return the token (remove in production!)
    reset_link = f"http://localhost:3000/auth/reset-password?token={reset_token}"
    
    return {
        "message": "Password reset link sent",
        "reset_link": reset_link,  # Remove in production!
        "token": reset_token,  # Remove in production!
    }


@enhanced_router.post("/password/reset/confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest, client_ip: str = Depends(lambda: "unknown")):
    """Confirm password reset with token."""
    if not check_rate_limit(client_ip, "password_reset_confirm"):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Find reset token
    if request.token not in password_reset_tokens:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    reset_data = password_reset_tokens[request.token]
    expires_at = datetime.fromisoformat(reset_data["expires_at"])
    
    if datetime.now(timezone.utc) > expires_at:
        del password_reset_tokens[request.token]
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user_id = reset_data["user_id"]
    if user_id not in users_db:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Update password
    users_db[user_id]["password_hash"] = hash_password(request.new_password)
    
    # Remove reset token
    del password_reset_tokens[request.token]
    
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
