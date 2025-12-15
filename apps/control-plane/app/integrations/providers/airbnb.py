"""
Airbnb Integration Provider
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def reservations_list(
    tenant_id: str,
    connection: Connection,
    listing_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List reservations from Airbnb.
    
    Returns list of reservations.
    """
    if connection.status.value != "connected":
        raise ValueError("Airbnb not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if listing_id:
            params["listing_id"] = listing_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        result = await nango.proxy(
            provider=Provider.AIRBNB.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="v2/reservations",
            params=params
        )
        
        log_operation(tenant_id, Provider.AIRBNB, "reservations_list", params, result)
        return result.get("reservations", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.AIRBNB, "reservations_list", params, error=str(e))
        raise


async def reservation_update(
    tenant_id: str,
    connection: Connection,
    reservation_id: str,
    status: Optional[str] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update reservation (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Airbnb not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "reservation_update"
    parameters = {
        "reservation_id": reservation_id,
        "status": status,
        "message": message
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Update Airbnb Reservation",
            "reservation_id": reservation_id,
            "status": status
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.AIRBNB,
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
        if message:
            update_data["message"] = message
        
        result = await nango.proxy(
            provider=Provider.AIRBNB.value,
            connection_id=connection.nango_connection_id,
            method="PATCH",
            endpoint=f"v2/reservations/{reservation_id}",
            json_data=update_data
        )
        
        log_operation(tenant_id, Provider.AIRBNB, operation, parameters, result)
        return result.get("reservation", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.AIRBNB, operation, parameters, error=str(e))
        raise
