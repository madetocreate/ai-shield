"""
Jane App Integration Provider
Practice Management System via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def patients_list(
    tenant_id: str,
    connection: Connection,
    limit: int = 50,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List patients from Jane App.
    
    Returns list of patients.
    """
    if connection.status.value != "connected":
        raise ValueError("Jane App not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if search:
            params["search"] = search
        
        result = await nango.proxy(
            provider=Provider.JANE_APP.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="patients",
            params=params
        )
        
        log_operation(tenant_id, Provider.JANE_APP, "patients_list", params, result)
        return result.get("data", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.JANE_APP, "patients_list", params, error=str(e))
        raise


async def appointments_list(
    tenant_id: str,
    connection: Connection,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List appointments from Jane App.
    
    Returns list of appointments.
    """
    if connection.status.value != "connected":
        raise ValueError("Jane App not connected")
    
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
            provider=Provider.JANE_APP.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="appointments",
            params=params
        )
        
        log_operation(tenant_id, Provider.JANE_APP, "appointments_list", params, result)
        return result.get("data", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.JANE_APP, "appointments_list", params, error=str(e))
        raise


async def appointment_create(
    tenant_id: str,
    connection: Connection,
    patient_id: str,
    start_time: str,
    duration: int = 30,
    treatment_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create appointment (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Jane App not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "appointment_create"
    parameters = {
        "patient_id": patient_id,
        "start_time": start_time,
        "duration": duration,
        "treatment_id": treatment_id
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Jane App Appointment",
            "patient_id": patient_id,
            "start_time": start_time,
            "duration": duration
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.JANE_APP,
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
            "patient_id": patient_id,
            "start_time": start_time,
            "duration": duration
        }
        if treatment_id:
            appointment_data["treatment_id"] = treatment_id
        
        result = await nango.proxy(
            provider=Provider.JANE_APP.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="appointments",
            json_data=appointment_data
        )
        
        log_operation(tenant_id, Provider.JANE_APP, operation, parameters, result)
        return result.get("data", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.JANE_APP, operation, parameters, error=str(e))
        raise
