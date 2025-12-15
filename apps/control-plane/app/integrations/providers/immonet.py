"""
Immonet Integration Provider
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def properties_list(
    tenant_id: str,
    connection: Connection,
    status: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """List properties from Immonet."""
    if connection.status.value != "connected":
        raise ValueError("Immonet not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await nango.proxy(
            provider=Provider.IMMONET.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="api/v1/realestate",
            params=params
        )
        
        log_operation(tenant_id, Provider.IMMONET, "properties_list", params, result)
        return result.get("realestate", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.IMMONET, "properties_list", params, error=str(e))
        raise


async def property_create(
    tenant_id: str,
    connection: Connection,
    title: str,
    address: Dict[str, Any],
    price: float,
    property_type: str = "apartment",
    rooms: Optional[int] = None,
    area: Optional[float] = None
) -> Dict[str, Any]:
    """Create property (write operation → requires approval)."""
    if connection.status.value != "connected":
        raise ValueError("Immonet not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "property_create"
    parameters = {
        "title": title,
        "address": address,
        "price": price,
        "property_type": property_type,
        "rooms": rooms,
        "area": area
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Immonet Property",
            "title": title,
            "address": address,
            "price": price
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.IMMONET,
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
        property_data = {
            "title": title,
            "address": address,
            "price": price,
            "propertyType": property_type
        }
        if rooms:
            property_data["rooms"] = rooms
        if area:
            property_data["area"] = area
        
        result = await nango.proxy(
            provider=Provider.IMMONET.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="api/v1/realestate",
            json_data=property_data
        )
        
        log_operation(tenant_id, Provider.IMMONET, operation, parameters, result)
        return result.get("realestate", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.IMMONET, operation, parameters, error=str(e))
        raise
