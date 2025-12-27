"""
Apple Push Notifications (APNs) Integration Provider
Push-Benachrichtigungen für iOS/macOS Apps via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def send_notification(
    tenant_id: str,
    connection: Connection,
    device_token: str,
    title: str,
    body: str,
    badge: Optional[int] = None,
    sound: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send push notification via Apple Push Notification Service (APNs).
    
    Write operation → requires approval.
    """
    if connection.status.value != "connected":
        raise ValueError("Apple Push Notifications not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "send_notification"
    parameters = {
        "device_token": device_token,
        "title": title,
        "body": body,
        "badge": badge,
        "sound": sound,
        "data": data or {}
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Send Apple Push Notification",
            "device_token": device_token[:20] + "...",
            "title": title,
            "body": body
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.APPLE_PUSH_NOTIFICATIONS,
            connection_id=connection.nango_connection_id,
            operation=operation,
            parameters=parameters,
            preview=preview
        )
        from ..approvals import save_approval_request
        save_approval_request(approval_request)
        return {
            "approval_required": True,
            "approval_request": approval_request.dict()
        }
    
    nango = get_nango_client()
    try:
        notification_data = {
            "aps": {
                "alert": {
                    "title": title,
                    "body": body
                }
            }
        }
        if badge is not None:
            notification_data["aps"]["badge"] = badge
        if sound:
            notification_data["aps"]["sound"] = sound
        if data:
            notification_data.update(data)
        
        result = await nango.proxy(
            provider_config_key=Provider.APPLE_PUSH_NOTIFICATIONS.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint=f"3/device/{device_token}",
            json_data=notification_data
        )
        
        log_operation(tenant_id, Provider.APPLE_PUSH_NOTIFICATIONS, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.APPLE_PUSH_NOTIFICATIONS, operation, parameters, error=str(e))
        raise


async def register_device(
    tenant_id: str,
    connection: Connection,
    device_token: str,
    device_type: str = "ios",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Register device for push notifications (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Apple Push Notifications not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "register_device"
    parameters = {
        "device_token": device_token,
        "device_type": device_type,
        "user_id": user_id
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Register Device for Apple Push Notifications",
            "device_token": device_token[:20] + "...",
            "device_type": device_type
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.APPLE_PUSH_NOTIFICATIONS,
            connection_id=connection.nango_connection_id,
            operation=operation,
            parameters=parameters,
            preview=preview
        )
        from ..approvals import save_approval_request
        save_approval_request(approval_request)
        return {
            "approval_required": True,
            "approval_request": approval_request.dict()
        }
    
    nango = get_nango_client()
    try:
        device_data = {
            "device_token": device_token,
            "device_type": device_type
        }
        if user_id:
            device_data["user_id"] = user_id
        
        result = await nango.proxy(
            provider_config_key=Provider.APPLE_PUSH_NOTIFICATIONS.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="devices",
            json_data=device_data
        )
        
        log_operation(tenant_id, Provider.APPLE_PUSH_NOTIFICATIONS, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.APPLE_PUSH_NOTIFICATIONS, operation, parameters, error=str(e))
        raise
