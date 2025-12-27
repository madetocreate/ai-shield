"""
Google Integration Provider

Google Calendar, Gmail, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def calendar_find_slots(
    tenant_id: str,
    connection: Connection,
    start_time: datetime,
    end_time: datetime,
    calendar_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find available time slots in Google Calendar.
    
    Returns list of available slots.
    """
    if connection.status.value != "connected":
        raise ValueError("Google Calendar not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        # Via Nango proxy to Google Calendar API
        params = {
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "singleEvents": True,
            "orderBy": "startTime"
        }
        if calendar_id:
            params["calendarId"] = calendar_id
        
        result = await nango.proxy(
            provider_config_key=Provider.GOOGLE.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="calendar/v3/freebusy",
            params=params
        )
        
        log_operation(tenant_id, Provider.GOOGLE, "calendar_find_slots", params, result)
        return result.get("calendars", {}).get(calendar_id or "primary", {}).get("busy", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.GOOGLE, "calendar_find_slots", params, error=str(e))
        raise


async def calendar_create_event(
    tenant_id: str,
    connection: Connection,
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create calendar event (write operation → requires approval).
    
    Returns approval request if approval required, otherwise created event.
    """
    if connection.status.value != "connected":
        raise ValueError("Google Calendar not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "calendar_create_event"
    parameters = {
        "summary": summary,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "description": description,
        "attendees": attendees or [],
        "calendar_id": calendar_id or "primary"
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Create Google Calendar Event",
            "summary": summary,
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "attendees": attendees or []
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.GOOGLE,
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
    
    # Execute directly (should not happen for write ops if policy is correct)
    nango = get_nango_client()
    try:
        event_data = {
            "summary": summary,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"}
        }
        if description:
            event_data["description"] = description
        if attendees:
            event_data["attendees"] = [{"email": email} for email in attendees]
        
        result = await nango.proxy(
            provider_config_key=Provider.GOOGLE.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint=f"calendar/v3/calendars/{calendar_id or 'primary'}/events",
            json_data=event_data
        )
        
        log_operation(tenant_id, Provider.GOOGLE, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.GOOGLE, operation, parameters, error=str(e))
        raise
