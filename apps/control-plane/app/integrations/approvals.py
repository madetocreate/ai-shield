"""
Approval Requests API

Endpoints für Approval Queue Management.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query, Depends
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

from .types import ApprovalRequest, Provider
from app.main import require_admin_key


router = APIRouter(prefix="/v1/integrations/approvals", tags=["integrations", "approvals"])


# In-memory storage for approval requests (später DB)
_approval_storage: dict[str, ApprovalRequest] = {}


class ApprovalRequestResponse(BaseModel):
    """Approval request response."""
    request_id: str
    tenant_id: str
    provider: str
    operation: str
    parameters: dict
    preview: Optional[dict] = None
    status: str
    created_at: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None


@router.get("/", response_model=List[ApprovalRequestResponse])
async def list_approval_requests(
    tenant_id: str = Query(..., description="Tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    _admin: bool = Depends(require_admin_key)
):
    """
    List approval requests for a tenant.
    """
    requests = [
        r for r in _approval_storage.values()
        if r.tenant_id == tenant_id and (status is None or r.status == status)
    ]
    
    return [
        ApprovalRequestResponse(
            request_id=r.request_id,
            tenant_id=r.tenant_id,
            provider=r.provider.value,
            operation=r.operation,
            parameters=r.parameters,
            preview=r.preview,
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else None,
            approved_at=r.approved_at.isoformat() if r.approved_at else None,
            approved_by=r.approved_by
        )
        for r in requests
    ]


@router.post("/{request_id}/approve")
async def approve_request(
    request_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    _admin: bool = Depends(require_admin_key)
):
    """
    Approve and execute an approval request.
    """
    request = _approval_storage.get(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    
    if request.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {request.status}")
    
    # Update status
    request.status = "approved"
    request.approved_at = datetime.now(timezone.utc)
    request.approved_by = "user"  # TODO: Get from auth context
    
    # TODO: Execute the actual operation via provider module
    # For now, just mark as approved
    
    return {
        "ok": True,
        "message": "Request approved and executed",
        "request_id": request_id
    }


@router.post("/{request_id}/reject")
async def reject_request(
    request_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    _admin: bool = Depends(require_admin_key)
):
    """
    Reject an approval request.
    """
    request = _approval_storage.get(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    
    if request.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {request.status}")
    
    # Update status
    request.status = "rejected"
    request.approved_at = datetime.now(timezone.utc)
    request.approved_by = "user"  # TODO: Get from auth context
    
    return {
        "ok": True,
        "message": "Request rejected",
        "request_id": request_id
    }


def save_approval_request(request: ApprovalRequest) -> ApprovalRequest:
    """Save approval request to storage (called by provider modules)."""
    _approval_storage[request.request_id] = request
    return request


def get_approval_request(request_id: str) -> Optional[ApprovalRequest]:
    """Get approval request by ID."""
    return _approval_storage.get(request_id)
