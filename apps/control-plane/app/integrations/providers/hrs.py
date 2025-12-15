"""
HRS Integration Provider
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def reservations_list(
    tenant_id: str,
    connection: Connection,
    hotel_id: Optional[str] = None,
    arrival_date: Optional[str] = None,
    departure_date: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List reservations from HRS.
    
    Returns list of reservations.
    """
    if connection.status.value != "connected":
        raise ValueError("HRS not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if hotel_id:
            params["hotelId"] = hotel_id
        if arrival_date:
            params["arrivalDate"] = arrival_date
        if departure_date:
            params["departureDate"] = departure_date
        
        result = await nango.proxy(
            provider=Provider.HRS.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="api/v1/bookings",
            params=params
        )
        
        log_operation(tenant_id, Provider.HRS, "reservations_list", params, result)
        return result.get("bookings", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.HRS, "reservations_list", params, error=str(e))
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
        raise ValueError("HRS not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "reservation_update"
    parameters = {
        "reservation_id": reservation_id,
        "status": status
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Update HRS Reservation",
            "reservation_id": reservation_id,
            "status": status
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.HRS,
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
            provider=Provider.HRS.value,
            connection_id=connection.nango_connection_id,
            method="PATCH",
            endpoint=f"api/v1/bookings/{reservation_id}",
            json_data=update_data
        )
        
        log_operation(tenant_id, Provider.HRS, operation, parameters, result)
        return result.get("booking", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.HRS, operation, parameters, error=str(e))
        raise
