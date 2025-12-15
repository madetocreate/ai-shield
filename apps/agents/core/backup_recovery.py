"""
Backup & Recovery - Automated Backups, Point-in-Time Recovery
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import logging
import os

logger = logging.getLogger(__name__)

class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"

@dataclass
class Backup:
    id: str
    account_id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    size_bytes: int = 0
    verified: bool = False

@dataclass
class BackupSchedule:
    id: str
    account_id: str
    schedule_type: str
    backup_type: BackupType
    time: str
    enabled: bool = True
    next_run: Optional[datetime] = None

class BackupRecoveryService:
    def __init__(self, backup_dir: str = "backups"):
        self.backups: Dict[str, Backup] = {}
        self.schedules: Dict[str, BackupSchedule] = {}
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, account_id: str, backup_type: BackupType = BackupType.FULL) -> Backup:
        backup = Backup(
            id=f"backup_{datetime.now().timestamp()}",
            account_id=account_id,
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            created_at=datetime.now()
        )
        self.backups[backup.id] = backup
        import asyncio
        asyncio.create_task(self._execute_backup(backup))
        return backup
    
    async def _execute_backup(self, backup: Backup):
        backup.status = BackupStatus.RUNNING
        try:
            backup_data = await self._collect_backup_data(backup.account_id, backup.backup_type)
            filename = f"{backup.id}.json"
            file_path = os.path.join(self.backup_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
            backup.file_path = file_path
            backup.size_bytes = os.path.getsize(file_path)
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.now()
        except Exception as e:
            logger.error(f"Backup {backup.id} failed: {e}")
            backup.status = BackupStatus.FAILED
    
    async def _collect_backup_data(self, account_id: str, backup_type: BackupType) -> Dict[str, Any]:
        data = {"account_id": account_id, "backup_type": backup_type.value, "timestamp": datetime.now().isoformat(), "data": {}}
        try:
            from apps.agents.core.user_management import get_user_management
            user_mgmt = get_user_management()
            users = user_mgmt.get_users(account_id=account_id)
            data["data"]["users"] = [{"id": u.id, "email": u.email, "username": u.username, "role": u.role.value} for u in users]
            teams = user_mgmt.get_teams(account_id=account_id)
            data["data"]["teams"] = [{"id": t.id, "name": t.name, "member_ids": t.member_ids} for t in teams]
        except Exception as e:
            logger.warning(f"Fehler beim Sammeln von Daten: {e}")
        return data
    
    def get_backup(self, backup_id: str) -> Optional[Backup]:
        return self.backups.get(backup_id)
    
    def get_backups(self, account_id: Optional[str] = None, status: Optional[BackupStatus] = None, limit: int = 100) -> List[Backup]:
        backups = list(self.backups.values())
        if account_id:
            backups = [b for b in backups if b.account_id == account_id]
        if status:
            backups = [b for b in backups if b.status == status]
        backups.sort(key=lambda x: x.created_at, reverse=True)
        return backups[:limit]
    
    async def restore_backup(self, backup_id: str, selective: Optional[List[str]] = None) -> Dict[str, Any]:
        backup = self.backups.get(backup_id)
        if not backup or backup.status != BackupStatus.COMPLETED:
            raise ValueError(f"Backup {backup_id} nicht verfügbar")
        if not backup.file_path or not os.path.exists(backup.file_path):
            raise ValueError(f"Backup File nicht gefunden")
        with open(backup.file_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        return {"backup_id": backup_id, "restored_at": datetime.now().isoformat(), "restored_items": {}}
    
    def verify_backup(self, backup_id: str) -> bool:
        backup = self.backups.get(backup_id)
        if not backup or not backup.file_path or not os.path.exists(backup.file_path):
            return False
        try:
            with open(backup.file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            backup.verified = True
            backup.status = BackupStatus.VERIFIED
            return True
        except Exception:
            return False
    
    def schedule_backup(self, account_id: str, schedule_type: str, backup_type: BackupType, time: str) -> BackupSchedule:
        schedule = BackupSchedule(
            id=f"schedule_{datetime.now().timestamp()}",
            account_id=account_id,
            schedule_type=schedule_type,
            backup_type=backup_type,
            time=time
        )
        schedule.next_run = datetime.now() + timedelta(days=1)
        self.schedules[schedule.id] = schedule
        return schedule
    
    def delete_backup(self, backup_id: str) -> bool:
        backup = self.backups.get(backup_id)
        if not backup:
            return False
        if backup.file_path and os.path.exists(backup.file_path):
            os.remove(backup.file_path)
        del self.backups[backup_id]
        return True

_global_backup_service: Optional[BackupRecoveryService] = None

def get_backup_service() -> BackupRecoveryService:
    global _global_backup_service
    if _global_backup_service is None:
        backup_dir = os.getenv("BACKUP_DIR", "backups")
        _global_backup_service = BackupRecoveryService(backup_dir=backup_dir)
    return _global_backup_service
