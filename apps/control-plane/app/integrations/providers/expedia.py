"""
Expedia Integration Provider
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def reservations_list(
    tenant_id: str,
    connection: Connection,
    property_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List reservations from Expedia.
    
    Returns list of reservations.
    """
    if connection.status.value != "connected":
        raise ValueError("Expedia not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if property_id:
            params["propertyId"] = property_id
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        result = await nango.proxy(
            provider=Provider.EXPEDIA.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="v3/properties/reservations",
            params=params
        )
        
        log_operation(tenant_id, Provider.EXPEDIA, "reservations_list", params, result)
        return result.get("reservations", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.EXPEDIA, "reservations_list", params, error=str(e))
        raise


async def reservation_update(
    tenant_id: str,
    connection: Connection,
    reservation_id: str,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update reservation (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Expedia not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "reservation_update"
    parameters = {
        "reservation_id": reservation_id,
        "status": status
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Update Expedia Reservation",
            "reservation_id": reservation_id,
            "status": status
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.EXPEDIA,
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
        update_data = {}
        if status:
            update_data["status"] = status
        
        result = await nango.proxy(
            provider=Provider.EXPEDIA.value,
            connection_id=connection.nango_connection_id,
            method="PATCH",
            endpoint=f"v3/reservations/{reservation_id}",
            json_data=update_data
        )
        
        log_operation(tenant_id, Provider.EXPEDIA, operation, parameters, result)
        return result.get("reservation", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.EXPEDIA, operation, parameters, error=str(e))
        raise
