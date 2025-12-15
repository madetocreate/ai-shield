"""
Backup & Recovery API Endpoints
"""
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from apps.agents.core.backup_recovery import get_backup_service, BackupType, BackupStatus

router = APIRouter(prefix="/api/v1/backup", tags=["backup"])

class CreateBackupRequest(BaseModel):
    account_id: str
    backup_type: str = "full"

class BackupResponse(BaseModel):
    id: str
    account_id: str
    backup_type: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    size_bytes: int
    verified: bool

class RestoreBackupRequest(BaseModel):
    selective: Optional[List[str]] = None

@router.post("", response_model=BackupResponse)
async def create_backup(request: CreateBackupRequest):
    service = get_backup_service()
    try:
        backup_type = BackupType(request.backup_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Backup Type: {request.backup_type}")
    backup = service.create_backup(request.account_id, backup_type)
    return BackupResponse(
        id=backup.id, account_id=backup.account_id, backup_type=backup.backup_type.value,
        status=backup.status.value, created_at=backup.created_at.isoformat(),
        completed_at=backup.completed_at.isoformat() if backup.completed_at else None,
        size_bytes=backup.size_bytes, verified=backup.verified
    )

@router.get("", response_model=List[BackupResponse])
async def get_backups(account_id: Optional[str] = Query(None), status: Optional[str] = Query(None), limit: int = Query(100, le=1000)):
    service = get_backup_service()
    status_enum = None
    if status:
        try:
            status_enum = BackupStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Status: {status}")
    backups = service.get_backups(account_id=account_id, status=status_enum, limit=limit)
    return [BackupResponse(id=b.id, account_id=b.account_id, backup_type=b.backup_type.value, status=b.status.value,
                          created_at=b.created_at.isoformat(), completed_at=b.completed_at.isoformat() if b.completed_at else None,
                          size_bytes=b.size_bytes, verified=b.verified) for b in backups]

@router.get("/{backup_id}", response_model=BackupResponse)
async def get_backup(backup_id: str):
    service = get_backup_service()
    backup = service.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    return BackupResponse(id=backup.id, account_id=backup.account_id, backup_type=backup.backup_type.value,
                         status=backup.status.value, created_at=backup.created_at.isoformat(),
                         completed_at=backup.completed_at.isoformat() if backup.completed_at else None,
                         size_bytes=backup.size_bytes, verified=backup.verified)

@router.post("/{backup_id}/restore")
async def restore_backup(backup_id: str, request: RestoreBackupRequest):
    service = get_backup_service()
    try:
        result = await service.restore_backup(backup_id, selective=request.selective)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{backup_id}/verify")
async def verify_backup(backup_id: str):
    service = get_backup_service()
    verified = service.verify_backup(backup_id)
    if not verified:
        raise HTTPException(status_code=400, detail="Backup Verification fehlgeschlagen")
    return {"success": True, "verified": True}

@router.delete("/{backup_id}")
async def delete_backup(backup_id: str):
    service = get_backup_service()
    success = service.delete_backup(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    return {"success": True}
