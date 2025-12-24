"""
Authentication API Endpoints
Google OAuth, Apple Sign In, Email/Password Authentication
"""
import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
import httpx
from app.apple_verify import verify_apple_id_token

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# Security
security = HTTPBearer()

# Environment Variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
MICROSOFT_CLIENT_ID = os.environ.get("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET = os.environ.get("MICROSOFT_CLIENT_SECRET", "")
APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID", "")
APPLE_TEAM_ID = os.environ.get("APPLE_TEAM_ID", "")
APPLE_KEY_ID = os.environ.get("APPLE_KEY_ID", "")
APPLE_PRIVATE_KEY = os.environ.get("APPLE_PRIVATE_KEY", "")

# JWT_SECRET: Production must fail if missing, Dev can use fallback with warning
APP_ENV = os.environ.get("APP_ENV", os.environ.get("ENVIRONMENT", "production")).lower()
JWT_SECRET_ENV = os.environ.get("JWT_SECRET", "")

if not JWT_SECRET_ENV:
    if APP_ENV == "production":
        import sys
        print("ERROR: JWT_SECRET environment variable is required in production", file=sys.stderr)
        sys.exit(1)
    else:
        # Dev-only fallback: generate insecure temporary secret
        JWT_SECRET = secrets.token_urlsafe(32)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "⚠️  DEV ONLY / INSECURE: JWT_SECRET not set, using dynamically generated secret. "
            "This secret will change on every restart. Set JWT_SECRET in environment for stable tokens."
        )
else:
    JWT_SECRET = JWT_SECRET_ENV

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# In-memory user storage (TODO: Replace with database)
users_db: Dict[str, Dict[str, Any]] = {}
sessions_db: Dict[str, Dict[str, Any]] = {}
password_reset_tokens: Dict[str, Dict[str, Any]] = {}  # token -> {user_id, expires_at}


# Request/Response Models
class EmailSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleOAuthRequest(BaseModel):
    code: str
    redirect_uri: str


class MicrosoftOAuthRequest(BaseModel):
    code: str
    redirect_uri: str


class AppleSignInRequest(BaseModel):
    id_token: str
    user: Optional[Dict[str, Any]] = None  # Apple user info (first time only)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UserInfo(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str  # "email", "google", "apple"
    created_at: str


# Helper Functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt (secure, production-ready)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password using bcrypt."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        # Backward compatibility: Try SHA256 for old passwords (migration)
        import hashlib
        old_hash = hashlib.sha256(password.encode()).hexdigest()
        return old_hash == hashed


def create_jwt_token(user_id: str, email: str, refresh: bool = False) -> str:
    """Create JWT token."""
    # Refresh tokens last 30 days, access tokens 7 days
    expiration_hours = 24 * 30 if refresh else JWT_EXPIRATION_HOURS
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expiration_hours),
        "iat": datetime.now(timezone.utc),
        "type": "refresh" if refresh else "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    return users_db[user_id]


# Google OAuth
async def verify_google_token(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange Google OAuth code for user info."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google OAuth code")
        
        token_info = token_response.json()
        access_token = token_info.get("access_token")
        
        # Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        user_response = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Google user info")
        
        return user_response.json()


# Microsoft OAuth
async def verify_microsoft_token(code: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange Microsoft OAuth code for user info."""
    if not MICROSOFT_CLIENT_ID or not MICROSOFT_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Microsoft OAuth not configured")
    
    # Exchange code for token
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    token_data = {
        "code": code,
        "client_id": MICROSOFT_CLIENT_ID,
        "client_secret": MICROSOFT_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "scope": "openid email profile",
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Microsoft OAuth code")
        
        token_info = token_response.json()
        access_token = token_info.get("access_token")
        
        # Get user info from Microsoft Graph API
        user_info_url = "https://graph.microsoft.com/v1.0/me"
        user_response = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Microsoft user info")
        
        user_data = user_response.json()
        
        # Format to match expected structure
        return {
            "id": user_data.get("id"),
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "name": user_data.get("displayName"),
            "given_name": user_data.get("givenName"),
            "family_name": user_data.get("surname"),
            "picture": None,  # Microsoft Graph doesn't provide picture in /me endpoint
        }


# Apple Sign In
async def verify_apple_token(id_token: str) -> Dict[str, Any]:
    """Verify Apple ID token with JWKS signature verification."""
    # Use the new secure verification module
    return await verify_apple_id_token(id_token)


# API Endpoints
@router.post("/signup/email", response_model=AuthResponse)
async def signup_email(request: EmailSignupRequest):
    """Sign up with email and password."""
    # Check if user exists
    for user_id, user in users_db.items():
        if user.get("email") == request.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = secrets.token_urlsafe(16)
    user = {
        "id": user_id,
        "email": request.email,
        "name": request.name or request.email.split("@")[0],
        "password_hash": hash_password(request.password),
        "provider": "email",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "picture": None,
    }
    users_db[user_id] = user
    
    # Create tokens
    access_token = create_jwt_token(user_id, request.email, refresh=False)
    refresh_token = create_jwt_token(user_id, request.email, refresh=True)
    
    # Store refresh token
    sessions_db[refresh_token] = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": user_id,
            "email": request.email,
            "name": user["name"],
            "picture": None,
            "provider": "email",
        }
    )


@router.post("/login/email", response_model=AuthResponse)
async def login_email(request: EmailLoginRequest):
    """Login with email and password."""
    # Find user
    user = None
    for user_id, u in users_db.items():
        if u.get("email") == request.email and u.get("provider") == "email":
            if verify_password(request.password, u.get("password_hash", "")):
                user = u
                break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create tokens
    access_token = create_jwt_token(user["id"], request.email, refresh=False)
    refresh_token = create_jwt_token(user["id"], request.email, refresh=True)
    
    # Store refresh token
    sessions_db[refresh_token] = {
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name"),
            "picture": user.get("picture"),
            "provider": "email",
        }
    )


@router.post("/login/google", response_model=AuthResponse)
async def login_google(request: GoogleOAuthRequest):
    """Login/Signup with Google OAuth."""
    # Verify Google token
    google_user = await verify_google_token(request.code, request.redirect_uri)
    
    email = google_user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")
    
    # Find or create user
    user = None
    user_id = None
    
    for uid, u in users_db.items():
        if u.get("email") == email and u.get("provider") == "google":
            user = u
            user_id = uid
            break
    
    if not user:
        # Create new user
        user_id = secrets.token_urlsafe(16)
        user = {
            "id": user_id,
            "email": email,
            "name": google_user.get("name", email.split("@")[0]),
            "picture": google_user.get("picture"),
            "provider": "google",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        users_db[user_id] = user
    
    # Create tokens
    access_token = create_jwt_token(user_id, email, refresh=False)
    refresh_token = create_jwt_token(user_id, email, refresh=True)
    
    # Store refresh token
    sessions_db[refresh_token] = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": user_id,
            "email": email,
            "name": user.get("name"),
            "picture": user.get("picture"),
            "provider": "google",
        }
    )


@router.post("/login/microsoft", response_model=AuthResponse)
async def login_microsoft(request: MicrosoftOAuthRequest):
    """Login/Signup with Microsoft OAuth."""
    # Verify Microsoft token
    microsoft_user = await verify_microsoft_token(request.code, request.redirect_uri)
    
    email = microsoft_user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Microsoft account has no email")
    
    # Find or create user
    user = None
    user_id = None
    
    for uid, u in users_db.items():
        if u.get("email") == email and u.get("provider") == "microsoft":
            user = u
            user_id = uid
            break
    
    if not user:
        # Create new user
        user_id = secrets.token_urlsafe(16)
        user = {
            "id": user_id,
            "email": email,
            "name": microsoft_user.get("name") or microsoft_user.get("displayName") or email.split("@")[0],
            "picture": microsoft_user.get("picture"),
            "provider": "microsoft",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        users_db[user_id] = user
    
    # Create tokens
    access_token = create_jwt_token(user_id, email, refresh=False)
    refresh_token = create_jwt_token(user_id, email, refresh=True)
    
    # Store refresh token
    sessions_db[refresh_token] = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": user_id,
            "email": email,
            "name": user.get("name"),
            "picture": user.get("picture"),
            "provider": "microsoft",
        }
    )


@router.post("/login/apple", response_model=AuthResponse)
async def login_apple(request: AppleSignInRequest):
    """Login/Signup with Apple Sign In."""
    # Verify Apple token
    apple_user = await verify_apple_token(request.id_token)
    
    apple_user_id = apple_user.get("sub")
    email = apple_user.get("email")
    
    if not apple_user_id:
        raise HTTPException(status_code=400, detail="Invalid Apple token")
    
    # Find or create user
    user = None
    user_id = None
    
    # First, try to find by Apple user ID
    for uid, u in users_db.items():
        if u.get("apple_user_id") == apple_user_id:
            user = u
            user_id = uid
            break
    
    # If not found, try by email
    if not user and email:
        for uid, u in users_db.items():
            if u.get("email") == email and u.get("provider") == "apple":
                user = u
                user_id = uid
                # Update Apple user ID
                user["apple_user_id"] = apple_user_id
                break
    
    if not user:
        # Create new user
        user_id = secrets.token_urlsafe(16)
        name = None
        if request.user:
            name = request.user.get("name", {}).get("firstName", "")
            if request.user.get("name", {}).get("lastName"):
                name += " " + request.user.get("name", {}).get("lastName", "")
        
        user = {
            "id": user_id,
            "email": email or f"{apple_user_id}@apple.private",  # Apple may not provide email
            "name": name or "Apple User",
            "picture": None,
            "provider": "apple",
            "apple_user_id": apple_user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        users_db[user_id] = user
    
    # Create tokens
    access_token = create_jwt_token(user_id, user["email"], refresh=False)
    refresh_token = create_jwt_token(user_id, user["email"], refresh=True)
    
    # Store refresh token
    sessions_db[refresh_token] = {
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": user_id,
            "email": user["email"],
            "name": user.get("name"),
            "picture": user.get("picture"),
            "provider": "apple",
        }
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user info."""
    return UserInfo(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user.get("name"),
        picture=current_user.get("picture"),
        provider=current_user.get("provider", "email"),
        created_at=current_user.get("created_at", datetime.now(timezone.utc).isoformat()),
    )


@router.get("/google/authorize")
async def google_authorize_url():
    """Get Google OAuth authorization URL."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:3000/auth/callback/google")
    scope = "openid email profile"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    return {"auth_url": auth_url}


@router.get("/microsoft/authorize")
async def microsoft_authorize_url():
    """Get Microsoft OAuth authorization URL."""
    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Microsoft OAuth not configured")
    
    redirect_uri = os.environ.get("MICROSOFT_REDIRECT_URI", "http://localhost:3000/auth/callback/microsoft")
    scope = "openid email profile"
    
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={MICROSOFT_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&response_mode=query"
    )
    
    return {"auth_url": auth_url}


@router.get("/apple/authorize")
async def apple_authorize_url():
    """Get Apple Sign In authorization URL."""
    if not APPLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Apple Sign In not configured")
    
    redirect_uri = os.environ.get("APPLE_REDIRECT_URI", "http://localhost:3000/auth/callback/apple")
    scope = "name email"
    
    auth_url = (
        f"https://appleid.apple.com/auth/authorize"
        f"?client_id={APPLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code id_token"
        f"&scope={scope}"
        f"&response_mode=form_post"
    )
    
    return {"auth_url": auth_url}
