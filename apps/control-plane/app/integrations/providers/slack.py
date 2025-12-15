"""
Slack Integration Provider

Slack Messages, Channels, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def channels_list(
    tenant_id: str,
    connection: Connection,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List Slack channels.
    
    Returns list of channels.
    """
    if connection.status.value != "connected":
        raise ValueError("Slack not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        result = await nango.proxy(
            provider=Provider.SLACK.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="conversations.list",
            params=params
        )
        
        log_operation(tenant_id, Provider.SLACK, "channels_list", params, result)
        return result.get("channels", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.SLACK, "channels_list", params, error=str(e))
        raise


async def message_send(
    tenant_id: str,
    connection: Connection,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send Slack message (write operation → requires approval).
    
    Returns approval request if approval required, otherwise sent message info.
    """
    if connection.status.value != "connected":
        raise ValueError("Slack not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "message_send"
    parameters = {
        "channel": channel,
        "text": text,
        "thread_ts": thread_ts
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Send Slack Message",
            "channel": channel,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "is_thread": thread_ts is not None
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.SLACK,
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
    
    # Execute directly (should not happen for write ops)
    nango = get_nango_client()
    try:
        message_data = {
            "channel": channel,
            "text": text
        }
        if thread_ts:
            message_data["thread_ts"] = thread_ts
        
        result = await nango.proxy(
            provider=Provider.SLACK.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="chat.postMessage",
            json_data=message_data
        )
        
        log_operation(tenant_id, Provider.SLACK, operation, parameters, result)
        return result.get("message", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.SLACK, operation, parameters, error=str(e))
        raise
