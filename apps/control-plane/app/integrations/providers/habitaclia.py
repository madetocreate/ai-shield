"""
Habitaclia Integration Provider (Spain)
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def properties_list(
    tenant_id: str,
    connection: Connection,
    operation: Optional[str] = None,
    property_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """List properties from Habitaclia."""
    if connection.status.value != "connected":
        raise ValueError("Habitaclia not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if operation:
            params["operation"] = operation
        if property_type:
            params["propertyType"] = property_type
        
        result = await nango.proxy(
            provider=Provider.HABITACLIA.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="api/v1/properties",
            params=params
        )
        
        log_operation(tenant_id, Provider.HABITACLIA, "properties_list", params, result)
        return result.get("properties", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.HABITACLIA, "properties_list", params, error=str(e))
        raise


async def property_create(
    tenant_id: str,
    connection: Connection,
    title: str,
    address: Dict[str, Any],
    price: float,
    operation: str = "sale",
    property_type: str = "flat",
    rooms: Optional[int] = None,
    area: Optional[float] = None
) -> Dict[str, Any]:
    """Create property (write operation → requires approval)."""
    if connection.status.value != "connected":
        raise ValueError("Habitaclia not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation_name = "property_create"
    parameters = {
        "title": title,
        "address": address,
        "price": price,
        "operation": operation,
        "property_type": property_type,
        "rooms": rooms,
        "area": area
    }
    
    if requires_approval(operation_name):
        preview = {
            "action": "Create Habitaclia Property",
            "title": title,
            "address": address,
            "price": price,
            "operation": operation
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.HABITACLIA,
            connection_id=connection.nango_connection_id,
            operation=operation_name,
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
            "operation": operation,
            "propertyType": property_type
        }
        if rooms:
            property_data["rooms"] = rooms
        if area:
            property_data["size"] = area
        
        result = await nango.proxy(
            provider=Provider.HABITACLIA.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="api/v1/properties",
            json_data=property_data
        )
        
        log_operation(tenant_id, Provider.HABITACLIA, operation_name, parameters, result)
        return result.get("property", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.HABITACLIA, operation_name, parameters, error=str(e))
        raise
