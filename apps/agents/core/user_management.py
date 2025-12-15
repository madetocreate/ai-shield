"""
User Management & Teams - User CRUD, Teams, Roles, Permissions, Activity Log
"""
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import hashlib
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    MANAGER = "manager"

class Permission(Enum):
    AGENT_VIEW = "agent:view"
    AGENT_CREATE = "agent:create"
    AGENT_EDIT = "agent:edit"
    AGENT_DELETE = "agent:delete"
    ACCOUNT_VIEW = "account:view"
    ACCOUNT_EDIT = "account:edit"
    TEAM_VIEW = "team:view"
    TEAM_CREATE = "team:create"
    REPORT_VIEW = "report:view"
    ADMIN_ALL = "admin:all"

@dataclass
class User:
    id: str
    email: str
    username: str
    password_hash: str
    account_id: str
    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    team_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Team:
    id: str
    name: str
    account_id: str
    member_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ActivityLog:
    id: str
    user_id: str
    account_id: str
    action: str
    resource_type: str
    timestamp: datetime = field(default_factory=datetime.now)

class UserManagementService:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.teams: Dict[str, Team] = {}
        self.activity_logs: List[ActivityLog] = []
        self.role_permissions = {
            UserRole.ADMIN: {Permission.ADMIN_ALL},
            UserRole.MANAGER: {Permission.AGENT_VIEW, Permission.AGENT_CREATE, Permission.ACCOUNT_VIEW},
            UserRole.USER: {Permission.AGENT_VIEW, Permission.ACCOUNT_VIEW},
            UserRole.VIEWER: {Permission.AGENT_VIEW}
        }
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email: str, username: str, password: str, account_id: str, role: UserRole = UserRole.USER) -> User:
        user = User(
            id=f"user_{datetime.now().timestamp()}",
            email=email,
            username=username,
            password_hash=self._hash_password(password),
            account_id=account_id,
            role=role,
            permissions=self.role_permissions.get(role, set()).copy()
        )
        self.users[user.id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not user.is_active:
            return None
        if user.password_hash != self._hash_password(password):
            return None
        user.last_login = datetime.now()
        return user
    
    def create_team(self, name: str, account_id: str, created_by: str = "") -> Team:
        team = Team(
            id=f"team_{datetime.now().timestamp()}",
            name=name,
            account_id=account_id
        )
        self.teams[team.id] = team
        return team
    
    def get_users(self, account_id: Optional[str] = None) -> List[User]:
        if account_id:
            return [u for u in self.users.values() if u.account_id == account_id]
        return list(self.users.values())
    
    def get_teams(self, account_id: Optional[str] = None) -> List[Team]:
        if account_id:
            return [t for t in self.teams.values() if t.account_id == account_id]
        return list(self.teams.values())
    
    def log_activity(self, user_id: str, account_id: str, action: str, resource_type: str) -> ActivityLog:
        log = ActivityLog(
            id=f"log_{datetime.now().timestamp()}",
            user_id=user_id,
            account_id=account_id,
            action=action,
            resource_type=resource_type
        )
        self.activity_logs.append(log)
        if len(self.activity_logs) > 10000:
            self.activity_logs = self.activity_logs[-10000:]
        return log

_global_user_management: Optional[UserManagementService] = None

def get_user_management() -> UserManagementService:
    global _global_user_management
    if _global_user_management is None:
        _global_user_management = UserManagementService()
    return _global_user_management
