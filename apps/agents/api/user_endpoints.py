"""
User Management API Endpoints
"""
from fastapi import APIRouter, HTTPException, Body, Query, Header
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from apps.agents.core.user_management import get_user_management, UserRole

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    account_id: str
    role: str = "user"

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    account_id: str
    role: str
    is_active: bool
    team_ids: List[str]
    created_at: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user: UserResponse
    token: str

class CreateTeamRequest(BaseModel):
    name: str
    account_id: str

class TeamResponse(BaseModel):
    id: str
    name: str
    account_id: str
    member_ids: List[str]
    created_at: str

@router.post("", response_model=UserResponse)
async def create_user(request: CreateUserRequest):
    service = get_user_management()
    if service.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email bereits vergeben")
    try:
        role = UserRole(request.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Rolle: {request.role}")
    user = service.create_user(request.email, request.username, request.password, request.account_id, role)
    return UserResponse(
        id=user.id, email=user.email, username=user.username, account_id=user.account_id,
        role=user.role.value, is_active=user.is_active, team_ids=user.team_ids,
        created_at=user.created_at.isoformat()
    )

@router.get("", response_model=List[UserResponse])
async def get_users(account_id: Optional[str] = Query(None)):
    service = get_user_management()
    users = service.get_users(account_id=account_id)
    return [UserResponse(id=u.id, email=u.email, username=u.username, account_id=u.account_id,
                        role=u.role.value, is_active=u.is_active, team_ids=u.team_ids,
                        created_at=u.created_at.isoformat()) for u in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    service = get_user_management()
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    return UserResponse(id=user.id, email=user.email, username=user.username, account_id=user.account_id,
                       role=user.role.value, is_active=user.is_active, team_ids=user.team_ids,
                       created_at=user.created_at.isoformat())

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    service = get_user_management()
    user = service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Ungültige Credentials")
    token = f"token_{user.id}_{datetime.now().timestamp()}"
    return LoginResponse(
        user=UserResponse(id=user.id, email=user.email, username=user.username, account_id=user.account_id,
                         role=user.role.value, is_active=user.is_active, team_ids=user.team_ids,
                         created_at=user.created_at.isoformat()),
        token=token
    )

@router.post("/teams", response_model=TeamResponse)
async def create_team(request: CreateTeamRequest, x_user_id: Optional[str] = Header(None)):
    service = get_user_management()
    team = service.create_team(request.name, request.account_id, created_by=x_user_id or "")
    return TeamResponse(id=team.id, name=team.name, account_id=team.account_id,
                      member_ids=team.member_ids, created_at=team.created_at.isoformat())

@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(account_id: Optional[str] = Query(None)):
    service = get_user_management()
    teams = service.get_teams(account_id=account_id)
    return [TeamResponse(id=t.id, name=t.name, account_id=t.account_id, member_ids=t.member_ids,
                        created_at=t.created_at.isoformat()) for t in teams]
