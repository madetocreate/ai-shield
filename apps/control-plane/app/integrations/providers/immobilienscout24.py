"""
Immobilienscout24 Integration Provider
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
    """
    List properties from Immobilienscout24.
    
    Returns list of properties.
    """
    if connection.status.value != "connected":
        raise ValueError("Immobilienscout24 not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await nango.proxy(
            provider=Provider.IMMOBILIENSCOUT24.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="v1/realestate",
            params=params
        )
        
        log_operation(tenant_id, Provider.IMMOBILIENSCOUT24, "properties_list", params, result)
        return result.get("realestates", {}).get("realestate", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.IMMOBILIENSCOUT24, "properties_list", params, error=str(e))
        raise


async def property_create(
    tenant_id: str,
    connection: Connection,
    title: str,
    address: Dict[str, Any],
    price: float,
    rooms: Optional[int] = None,
    area: Optional[float] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create property (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Immobilienscout24 not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "property_create"
    parameters = {
        "title": title,
        "address": address,
        "price": price,
        "rooms": rooms,
        "area": area,
        "description": description
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create Immobilienscout24 Property",
            "title": title,
            "address": address,
            "price": price
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.IMMOBILIENSCOUT24,
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
            "realestate": {
                "title": title,
                "address": address,
                "price": price
            }
        }
        if rooms:
            property_data["realestate"]["rooms"] = rooms
        if area:
            property_data["realestate"]["area"] = area
        if description:
            property_data["realestate"]["description"] = description
        
        result = await nango.proxy(
            provider=Provider.IMMOBILIENSCOUT24.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="v1/realestate",
            json_data=property_data
        )
        
        log_operation(tenant_id, Provider.IMMOBILIENSCOUT24, operation, parameters, result)
        return result.get("realestate", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.IMMOBILIENSCOUT24, operation, parameters, error=str(e))
        raise


async def property_update(
    tenant_id: str,
    connection: Connection,
    property_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update property (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("Immobilienscout24 not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "property_update"
    parameters = {
        "property_id": property_id,
        "updates": updates
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Update Immobilienscout24 Property",
            "property_id": property_id,
            "updates": updates
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.IMMOBILIENSCOUT24,
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
        result = await nango.proxy(
            provider=Provider.IMMOBILIENSCOUT24.value,
            connection_id=connection.nango_connection_id,
            method="PATCH",
            endpoint=f"v1/realestate/{property_id}",
            json_data=updates
        )
        
        log_operation(tenant_id, Provider.IMMOBILIENSCOUT24, operation, parameters, result)
        return result.get("realestate", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.IMMOBILIENSCOUT24, operation, parameters, error=str(e))
        raise
