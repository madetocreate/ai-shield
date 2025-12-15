"""
Epic MyChart Integration Provider
EHR Integration via Nango (FHIR API).
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def patients_list(
    tenant_id: str,
    connection: Connection,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List patients from Epic MyChart (FHIR).
    
    Returns list of patients.
    """
    if connection.status.value != "connected":
        raise ValueError("Epic MyChart not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"_count": limit}
        
        result = await nango.proxy(
            provider=Provider.EPIC_MYCHART.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="fhir/Patient",
            params=params
        )
        
        log_operation(tenant_id, Provider.EPIC_MYCHART, "patients_list", params, result)
        return result.get("entry", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.EPIC_MYCHART, "patients_list", params, error=str(e))
        raise


async def appointments_list(
    tenant_id: str,
    connection: Connection,
    patient_id: Optional[str] = None,
    start_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List appointments from Epic MyChart (FHIR).
    
    Returns list of appointments.
    """
    if connection.status.value != "connected":
        raise ValueError("Epic MyChart not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {}
        if patient_id:
            params["patient"] = patient_id
        if start_date:
            params["date"] = f"ge{start_date}"
        
        result = await nango.proxy(
            provider=Provider.EPIC_MYCHART.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="fhir/Appointment",
            params=params
        )
        
        log_operation(tenant_id, Provider.EPIC_MYCHART, "appointments_list", params, result)
        return result.get("entry", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.EPIC_MYCHART, "appointments_list", params, error=str(e))
        raise


async def appointment_create(
    tenant_id: str,
    connection: Connection,
    patient_id: str,
    start_time: str,
    duration: int = 30,
    service_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create appointment (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Epic MyChart not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "appointment_create"
    parameters = {
        "patient_id": patient_id,
        "start_time": start_time,
        "duration": duration,
        "service_type": service_type
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Epic MyChart Appointment",
            "patient_id": patient_id,
            "start_time": start_time,
            "duration": duration
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.EPIC_MYCHART,
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
        # FHIR Appointment resource
        appointment_data = {
            "resourceType": "Appointment",
            "status": "proposed",
            "participant": [
                {
                    "actor": {
                        "reference": f"Patient/{patient_id}"
                    },
                    "status": "accepted"
                }
            ],
            "start": start_time,
            "minutesDuration": duration
        }
        if service_type:
            appointment_data["serviceType"] = [{"text": service_type}]
        
        result = await nango.proxy(
            provider=Provider.EPIC_MYCHART.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="fhir/Appointment",
            json_data=appointment_data
        )
        
        log_operation(tenant_id, Provider.EPIC_MYCHART, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.EPIC_MYCHART, operation, parameters, error=str(e))
        raise
