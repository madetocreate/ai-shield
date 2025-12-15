"""
Notification System API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

from apps.agents.core.notifications import get_notification_service, NotificationChannel, NotificationPriority

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

class SendNotificationRequest(BaseModel):
    user_id: str
    account_id: str
    channel: str
    subject: Optional[str] = None
    body: str
    priority: str = "normal"

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    account_id: str
    channel: str
    subject: Optional[str]
    body: str
    priority: str
    status: str
    created_at: str

@router.post("", response_model=NotificationResponse)
async def send_notification(request: SendNotificationRequest):
    service = get_notification_service()
    try:
        channel = NotificationChannel(request.channel)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Channel: {request.channel}")
    try:
        priority = NotificationPriority(request.priority)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Priority: {request.priority}")
    notification = await service.send_notification(user_id=request.user_id, account_id=request.account_id, channel=channel, subject=request.subject, body=request.body, priority=priority)
    return NotificationResponse(id=notification.id, user_id=notification.user_id, account_id=notification.account_id, channel=notification.channel.value, subject=notification.subject, body=notification.body, priority=notification.priority.value, status=notification.status.value, created_at=notification.created_at.isoformat())

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(user_id: Optional[str] = Query(None), account_id: Optional[str] = Query(None), channel: Optional[str] = Query(None)):
    service = get_notification_service()
    notifications = list(service.notifications.values())
    if user_id:
        notifications = [n for n in notifications if n.user_id == user_id]
    if account_id:
        notifications = [n for n in notifications if n.account_id == account_id]
    if channel:
        try:
            channel_enum = NotificationChannel(channel)
            notifications = [n for n in notifications if n.channel == channel_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Channel: {channel}")
    return [NotificationResponse(id=n.id, user_id=n.user_id, account_id=n.account_id, channel=n.channel.value, subject=n.subject, body=n.body, priority=n.priority.value, status=n.status.value, created_at=n.created_at.isoformat()) for n in notifications]

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: str):
    service = get_notification_service()
    notification = service.notifications.get(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification nicht gefunden")
    return NotificationResponse(id=notification.id, user_id=notification.user_id, account_id=notification.account_id, channel=notification.channel.value, subject=notification.subject, body=notification.body, priority=notification.priority.value, status=notification.status.value, created_at=notification.created_at.isoformat())
