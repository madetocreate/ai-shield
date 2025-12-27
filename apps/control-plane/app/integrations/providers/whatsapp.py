"""
WhatsApp (Meta) Integration Provider

WhatsApp Business Messaging via Nango.
"""
from typing import Dict, Any, Optional
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def messages_send(
    tenant_id: str,
    connection: Connection,
    to: str,
    message: str,
    media_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send WhatsApp message (write operation → requires approval).
    
    Returns approval request if approval required, otherwise sent message info.
    """
    if connection.status.value != "connected":
        raise ValueError("WhatsApp not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "messages_send"
    parameters = {
        "to": to,
        "message": message,
        "media_url": media_url
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Send WhatsApp Message",
            "to": to,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "has_media": media_url is not None
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.WHATSAPP,
            connection_id=connection.nango_connection_id,
            operation=operation,
            parameters=parameters,
            preview=preview
        )
        # Save approval request
        from ..approvals import save_approval_request
        save_approval_request(approval_request)
        return {
            "approval_required": True,
            "approval_request": approval_request.dict()
        }
    
    # Execute directly (should not happen for write ops)
    nango = get_nango_client()
    try:
        message_data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        if media_url:
            message_data["type"] = "image"
            message_data["image"] = {"link": media_url}
        
        result = await nango.proxy(
            provider_config_key=Provider.WHATSAPP.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="v18.0/{phone-number-id}/messages",
            json_data=message_data
        )
        
        log_operation(tenant_id, Provider.WHATSAPP, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.WHATSAPP, operation, parameters, error=str(e))
        raise


async def webhook_receive(
    tenant_id: str,
    connection: Connection,
    webhook_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Receive and process WhatsApp webhook.
    
    This is called by your webhook endpoint when Meta sends events.
    """
    if connection.status.value != "connected":
        raise ValueError("WhatsApp not connected")
    
    # Process webhook data
    # TODO: Implement webhook processing logic
    log_operation(tenant_id, Provider.WHATSAPP, "webhook_receive", webhook_data)
    
    return {
        "status": "received",
        "processed": True
    }
