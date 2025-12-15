"""
iCloud Calendar Integration Provider
iCloud Calendar via CalDAV/OAuth via Nango.
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
    List calendar events from iCloud Calendar.
    
    Returns list of events.
    """
    if connection.status.value != "connected":
        raise ValueError("iCloud Calendar not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {}
        if start_time:
            params["start"] = start_time.isoformat()
        if end_time:
            params["end"] = end_time.isoformat()
        
        # iCloud Calendar uses CalDAV, but we can access via iCloud API
        endpoint = f"calendars/{calendar_id or 'default'}/events" if calendar_id else "calendars/default/events"
        
        result = await nango.proxy(
            provider=Provider.ICLOUD_CALENDAR.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint=endpoint,
            params=params
        )
        
        log_operation(tenant_id, Provider.ICLOUD_CALENDAR, "calendar_list_events", params, result)
        return result.get("events", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.ICLOUD_CALENDAR, "calendar_list_events", params, error=str(e))
        raise


async def calendar_create_event(
    tenant_id: str,
    connection: Connection,
    title: str,
    start_time: datetime,
    end_time: datetime,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create calendar event (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("iCloud Calendar not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "calendar_create_event"
    parameters = {
        "title": title,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "description": description,
        "location": location,
        "calendar_id": calendar_id or "default"
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create iCloud Calendar Event",
            "title": title,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.ICLOUD_CALENDAR,
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
            "title": title,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        if description:
            event_data["description"] = description
        if location:
            event_data["location"] = location
        
        endpoint = f"calendars/{calendar_id or 'default'}/events" if calendar_id else "calendars/default/events"
        
        result = await nango.proxy(
            provider=Provider.ICLOUD_CALENDAR.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint=endpoint,
            json_data=event_data
        )
        
        log_operation(tenant_id, Provider.ICLOUD_CALENDAR, operation, parameters, result)
        return result.get("event", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.ICLOUD_CALENDAR, operation, parameters, error=str(e))
        raise
