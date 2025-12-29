"""
Zendesk Integration Provider

Zendesk Tickets, Users, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def tickets_list(
    tenant_id: str,
    connection: Connection,
    status: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List Zendesk tickets.
    
    Returns list of tickets.
    """
    if connection.status.value != "connected":
        raise ValueError("Zendesk not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"per_page": limit}
        if status:
            params["status"] = status
        
        result = await nango.proxy(
            provider_config_key=Provider.ZENDESK.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="api/v2/tickets.json",
            params=params
        )
        
        log_operation(tenant_id, Provider.ZENDESK, "tickets_list", params, result)
        return result.get("tickets", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.ZENDESK, "tickets_list", params, error=str(e))
        raise


async def ticket_create(
    tenant_id: str,
    connection: Connection,
    subject: str,
    comment: str,
    requester_id: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create Zendesk ticket (write operation → requires approval).
    
    Returns approval request if approval required, otherwise created ticket.
    """
    if connection.status.value != "connected":
        raise ValueError("Zendesk not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "ticket_create"
    parameters = {
        "subject": subject,
        "comment": comment,
        "requester_id": requester_id,
        "priority": priority
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Create Zendesk Ticket",
            "subject": subject,
            "comment": comment[:100] + "..." if len(comment) > 100 else comment,
            "priority": priority or "normal"
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.ZENDESK,
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
        ticket_data = {
            "ticket": {
                "subject": subject,
                "comment": {"body": comment},
            }
        }
        if requester_id:
            ticket_data["ticket"]["requester_id"] = requester_id
        if priority:
            ticket_data["ticket"]["priority"] = priority
        
        result = await nango.proxy(
            provider_config_key=Provider.ZENDESK.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="api/v2/tickets.json",
            json_data=ticket_data
        )
        
        log_operation(tenant_id, Provider.ZENDESK, operation, parameters, result)
        return result.get("ticket", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.ZENDESK, operation, parameters, error=str(e))
        raise
