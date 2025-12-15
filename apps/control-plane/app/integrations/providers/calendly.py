"""
Calendly Integration Provider
Terminbuchung via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def events_list(
    tenant_id: str,
    connection: Connection,
    user: Optional[str] = None,
    invitee_email: Optional[str] = None,
    count: int = 20
) -> List[Dict[str, Any]]:
    """
    List Calendly events.
    
    Returns list of events.
    """
    if connection.status.value != "connected":
        raise ValueError("Calendly not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"count": count}
        if user:
            params["user"] = user
        if invitee_email:
            params["invitee_email"] = invitee_email
        
        result = await nango.proxy(
            provider=Provider.CALENDLY.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="scheduled_events",
            params=params
        )
        
        log_operation(tenant_id, Provider.CALENDLY, "events_list", params, result)
        return result.get("collection", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.CALENDLY, "events_list", params, error=str(e))
        raise


async def event_type_create(
    tenant_id: str,
    connection: Connection,
    name: str,
    duration: int = 30,
    kind: str = "standard",
    scheduling_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create event type (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Calendly not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "event_type_create"
    parameters = {
        "name": name,
        "duration": duration,
        "kind": kind,
        "scheduling_url": scheduling_url
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Calendly Event Type",
            "name": name,
            "duration": duration
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.CALENDLY,
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
        event_type_data = {
            "name": name,
            "duration": duration,
            "kind": kind
        }
        if scheduling_url:
            event_type_data["scheduling_url"] = scheduling_url
        
        result = await nango.proxy(
            provider=Provider.CALENDLY.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="event_types",
            json_data=event_type_data
        )
        
        log_operation(tenant_id, Provider.CALENDLY, operation, parameters, result)
        return result.get("resource", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.CALENDLY, operation, parameters, error=str(e))
        raise
