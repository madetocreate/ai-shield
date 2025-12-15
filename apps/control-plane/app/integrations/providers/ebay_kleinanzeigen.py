"""
eBay Kleinanzeigen Integration Provider
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
    """List properties from eBay Kleinanzeigen."""
    if connection.status.value != "connected":
        raise ValueError("eBay Kleinanzeigen not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await nango.proxy(
            provider=Provider.EBAY_KLEINANZEIGEN.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="api/v1/ads",
            params=params
        )
        
        log_operation(tenant_id, Provider.EBAY_KLEINANZEIGEN, "properties_list", params, result)
        return result.get("ads", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.EBAY_KLEINANZEIGEN, "properties_list", params, error=str(e))
        raise


async def property_create(
    tenant_id: str,
    connection: Connection,
    title: str,
    description: str,
    price: float,
    category: str = "real-estate",
    location: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create property listing (write operation → requires approval)."""
    if connection.status.value != "connected":
        raise ValueError("eBay Kleinanzeigen not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "property_create"
    parameters = {
        "title": title,
        "description": description,
        "price": price,
        "category": category,
        "location": location
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Create eBay Kleinanzeigen Listing",
            "title": title,
            "price": price,
            "category": category
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.EBAY_KLEINANZEIGEN,
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
        ad_data = {
            "title": title,
            "description": description,
            "price": price,
            "category": category
        }
        if location:
            ad_data["location"] = location
        
        result = await nango.proxy(
            provider=Provider.EBAY_KLEINANZEIGEN.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="api/v1/ads",
            json_data=ad_data
        )
        
        log_operation(tenant_id, Provider.EBAY_KLEINANZEIGEN, operation, parameters, result)
        return result.get("ad", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.EBAY_KLEINANZEIGEN, operation, parameters, error=str(e))
        raise
