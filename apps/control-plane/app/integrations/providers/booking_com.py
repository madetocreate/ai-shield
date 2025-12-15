"""
Booking.com Integration Provider
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def reservations_list(
    tenant_id: str,
    connection: Connection,
    check_in: Optional[str] = None,
    check_out: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List reservations from Booking.com.
    
    Returns list of reservations.
    """
    if connection.status.value != "connected":
        raise ValueError("Booking.com not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if check_in:
            params["check_in"] = check_in
        if check_out:
            params["check_out"] = check_out
        
        result = await nango.proxy(
            provider=Provider.BOOKING_COM.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="v3/bookings",
            params=params
        )
        
        log_operation(tenant_id, Provider.BOOKING_COM, "reservations_list", params, result)
        return result.get("bookings", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.BOOKING_COM, "reservations_list", params, error=str(e))
        raise


async def reservation_update(
    tenant_id: str,
    connection: Connection,
    reservation_id: str,
    status: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update reservation (write operation → requires approval).
    
    Returns approval request if approval required, otherwise updated reservation.
    """
    if connection.status.value != "connected":
        raise ValueError("Booking.com not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "reservation_update"
    parameters = {
        "reservation_id": reservation_id,
        "status": status,
        "notes": notes
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Update Booking.com Reservation",
            "reservation_id": reservation_id,
            "status": status,
            "notes": notes
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.BOOKING_COM,
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
    
    # Execute directly (should not happen for write ops)
    nango = get_nango_client()
    try:
        update_data = {}
        if status:
            update_data["status"] = status
        if notes:
            update_data["notes"] = notes
        
        result = await nango.proxy(
            provider=Provider.BOOKING_COM.value,
            connection_id=connection.nango_connection_id,
            method="PATCH",
            endpoint=f"v3/bookings/{reservation_id}",
            json_data=update_data
        )
        
        log_operation(tenant_id, Provider.BOOKING_COM, operation, parameters, result)
        return result.get("booking", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.BOOKING_COM, operation, parameters, error=str(e))
        raise
