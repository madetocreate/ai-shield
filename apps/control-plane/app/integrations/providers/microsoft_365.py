"""
Microsoft 365 Integration Provider
Outlook Calendar, Email, Teams via Nango.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def calendar_list_events(
    tenant_id: str,
    connection: Connection,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    calendar_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List calendar events from Microsoft 365 Outlook.
    
    Returns list of events.
    """
    if connection.status.value != "connected":
        raise ValueError("Microsoft 365 not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {}
        if start_time:
            params["startDateTime"] = start_time.isoformat()
        if end_time:
            params["endDateTime"] = end_time.isoformat()
        
        endpoint = f"v1.0/me/calendars/{calendar_id or 'calendar'}/events" if calendar_id else "v1.0/me/events"
        
        result = await nango.proxy(
            provider_config_key=Provider.MICROSOFT_365.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint=endpoint,
            params=params
        )
        
        log_operation(tenant_id, Provider.MICROSOFT_365, "calendar_list_events", params, result)
        return result.get("value", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.MICROSOFT_365, "calendar_list_events", params, error=str(e))
        raise


async def calendar_create_event(
    tenant_id: str,
    connection: Connection,
    subject: str,
    start_time: datetime,
    end_time: datetime,
    body: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create calendar event (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Microsoft 365 not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "calendar_create_event"
    parameters = {
        "subject": subject,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "body": body,
        "attendees": attendees or [],
        "calendar_id": calendar_id or "calendar"
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Microsoft 365 Calendar Event",
            "subject": subject,
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "attendees": attendees or []
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.MICROSOFT_365,
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
        event_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            }
        }
        if body:
            event_data["body"] = {"contentType": "HTML", "content": body}
        if attendees:
            event_data["attendees"] = [{"emailAddress": {"address": email}} for email in attendees]
        
        endpoint = f"v1.0/me/calendars/{calendar_id or 'calendar'}/events" if calendar_id else "v1.0/me/events"
        
        result = await nango.proxy(
            provider_config_key=Provider.MICROSOFT_365.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint=endpoint,
            json_data=event_data
        )
        
        log_operation(tenant_id, Provider.MICROSOFT_365, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.MICROSOFT_365, operation, parameters, error=str(e))
        raise
