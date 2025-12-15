"""
Doctolib Integration Provider
Terminbuchung (Europa) via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def appointments_list(
    tenant_id: str,
    connection: Connection,
    practice_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List appointments from Doctolib.
    
    Returns list of appointments.
    """
    if connection.status.value != "connected":
        raise ValueError("Doctolib not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {}
        if practice_id:
            params["practice_id"] = practice_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        result = await nango.proxy(
            provider=Provider.DOCTOLIB.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="appointments",
            params=params
        )
        
        log_operation(tenant_id, Provider.DOCTOLIB, "appointments_list", params, result)
        return result.get("appointments", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.DOCTOLIB, "appointments_list", params, error=str(e))
        raise


async def slots_list(
    tenant_id: str,
    connection: Connection,
    practice_id: str,
    agenda_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List available slots from Doctolib.
    
    Returns list of available slots.
    """
    if connection.status.value != "connected":
        raise ValueError("Doctolib not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {
            "practice_id": practice_id,
            "agenda_id": agenda_id
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        result = await nango.proxy(
            provider=Provider.DOCTOLIB.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="slots",
            params=params
        )
        
        log_operation(tenant_id, Provider.DOCTOLIB, "slots_list", params, result)
        return result.get("slots", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.DOCTOLIB, "slots_list", params, error=str(e))
        raise


async def appointment_create(
    tenant_id: str,
    connection: Connection,
    practice_id: str,
    agenda_id: str,
    slot_id: str,
    patient_first_name: str,
    patient_last_name: str,
    patient_email: str,
    patient_phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create appointment (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Doctolib not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "appointment_create"
    parameters = {
        "practice_id": practice_id,
        "agenda_id": agenda_id,
        "slot_id": slot_id,
        "patient_first_name": patient_first_name,
        "patient_last_name": patient_last_name,
        "patient_email": patient_email,
        "patient_phone": patient_phone
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Doctolib Appointment",
            "practice_id": practice_id,
            "patient_name": f"{patient_first_name} {patient_last_name}",
            "patient_email": patient_email
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.DOCTOLIB,
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
            "practice_id": practice_id,
            "agenda_id": agenda_id,
            "slot_id": slot_id,
            "patient": {
                "first_name": patient_first_name,
                "last_name": patient_last_name,
                "email": patient_email
            }
        }
        if patient_phone:
            appointment_data["patient"]["phone"] = patient_phone
        
        result = await nango.proxy(
            provider=Provider.DOCTOLIB.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="appointments",
            json_data=appointment_data
        )
        
        log_operation(tenant_id, Provider.DOCTOLIB, operation, parameters, result)
        return result.get("appointment", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.DOCTOLIB, operation, parameters, error=str(e))
        raise
