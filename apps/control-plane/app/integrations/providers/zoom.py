"""
Zoom Integration Provider
Video-Konsultationen und Telemedizin via Nango.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def meetings_list(
    tenant_id: str,
    connection: Connection,
    user_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List Zoom meetings.
    
    Returns list of meetings.
    """
    if connection.status.value != "connected":
        raise ValueError("Zoom not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        endpoint = f"users/{user_id or 'me'}/meetings" if user_id else "users/me/meetings"
        
        result = await nango.proxy(
            provider=Provider.ZOOM.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint=endpoint,
            params=params
        )
        
        log_operation(tenant_id, Provider.ZOOM, "meetings_list", params, result)
        return result.get("meetings", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.ZOOM, "meetings_list", params, error=str(e))
        raise


async def meeting_create(
    tenant_id: str,
    connection: Connection,
    topic: str,
    start_time: datetime,
    duration: int = 30,
    type: int = 2,  # Scheduled meeting
    settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create Zoom meeting (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Zoom not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "meeting_create"
    parameters = {
        "topic": topic,
        "start_time": start_time.isoformat(),
        "duration": duration,
        "type": type,
        "settings": settings or {}
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Zoom Meeting",
            "topic": topic,
            "start_time": start_time.isoformat(),
            "duration": duration
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.ZOOM,
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
        meeting_data = {
            "topic": topic,
            "type": type,
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration": duration
        }
        if settings:
            meeting_data["settings"] = settings
        
        result = await nango.proxy(
            provider=Provider.ZOOM.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="users/me/meetings",
            json_data=meeting_data
        )
        
        log_operation(tenant_id, Provider.ZOOM, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.ZOOM, operation, parameters, error=str(e))
        raise
