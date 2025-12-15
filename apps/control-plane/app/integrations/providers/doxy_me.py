"""
Doxy.me Integration Provider
Telemedizin-Plattform via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def appointments_list(
    tenant_id: str,
    connection: Connection,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List Doxy.me appointments.
    
    Returns list of appointments.
    """
    if connection.status.value != "connected":
        raise ValueError("Doxy.me not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        result = await nango.proxy(
            provider=Provider.DOXY_ME.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="appointments",
            params=params
        )
        
        log_operation(tenant_id, Provider.DOXY_ME, "appointments_list", params, result)
        return result.get("appointments", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.DOXY_ME, "appointments_list", params, error=str(e))
        raise


async def appointment_create(
    tenant_id: str,
    connection: Connection,
    patient_email: str,
    start_time: str,
    duration: int = 30,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create appointment (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Doxy.me not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "appointment_create"
    parameters = {
        "patient_email": patient_email,
        "start_time": start_time,
        "duration": duration,
        "notes": notes
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Doxy.me Appointment",
            "patient_email": patient_email,
            "start_time": start_time,
            "duration": duration
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.DOXY_ME,
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
        appointment_data = {
            "patient_email": patient_email,
            "start_time": start_time,
            "duration": duration
        }
        if notes:
            appointment_data["notes"] = notes
        
        result = await nango.proxy(
            provider=Provider.DOXY_ME.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="appointments",
            json_data=appointment_data
        )
        
        log_operation(tenant_id, Provider.DOXY_ME, operation, parameters, result)
        return result.get("appointment", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.DOXY_ME, operation, parameters, error=str(e))
        raise
