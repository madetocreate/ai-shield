"""
Notification System - Email, SMS, Push, In-App Notifications
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

@dataclass
class Notification:
    id: str
    user_id: str
    account_id: str
    channel: NotificationChannel
    subject: Optional[str] = None
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)

class NotificationService:
    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
    
    async def send_notification(self, user_id: str, account_id: str, channel: NotificationChannel, subject: Optional[str] = None, body: str = "", priority: NotificationPriority = NotificationPriority.NORMAL) -> Notification:
        notification = Notification(
            id=f"notif_{datetime.now().timestamp()}",
            user_id=user_id,
            account_id=account_id,
            channel=channel,
            subject=subject,
            body=body,
            priority=priority
        )
        self.notifications[notification.id] = notification
        return notification

_global_notification_service: Optional[NotificationService] = None

def get_notification_service() -> NotificationService:
    global _global_notification_service
    if _global_notification_service is None:
        _global_notification_service = NotificationService()
    return _global_notification_service
