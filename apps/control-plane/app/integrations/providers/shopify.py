"""
Shopify Integration Provider

Shopify Orders, Customers, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def orders_get_status(
    tenant_id: str,
    connection: Connection,
    order_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get Shopify order status.
    
    Returns list of orders or single order if order_id provided.
    """
    if connection.status.value != "connected":
        raise ValueError("Shopify not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        endpoint = f"admin/api/2024-01/orders/{order_id}.json" if order_id else "admin/api/2024-01/orders.json"
        params = {"limit": limit} if not order_id else {}
        
        result = await nango.proxy(
            provider_config_key=Provider.SHOPIFY.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint=endpoint,
            params=params
        )
        
        log_operation(tenant_id, Provider.SHOPIFY, "orders_get_status", {"order_id": order_id, "limit": limit}, result)
        
        if order_id:
            return result.get("order", {})
        return result.get("orders", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.SHOPIFY, "orders_get_status", {"order_id": order_id}, error=str(e))
        raise


async def draft_order_create(
    tenant_id: str,
    connection: Connection,
    line_items: List[Dict[str, Any]],
    customer_id: Optional[str] = None,
    note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create draft order (write operation → requires approval).
    
    Returns approval request if approval required, otherwise created draft order.
    """
    if connection.status.value != "connected":
        raise ValueError("Shopify not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "draft_order_create"
    parameters = {
        "line_items": line_items,
        "customer_id": customer_id,
        "note": note
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Create Shopify Draft Order",
            "line_items": line_items,
            "customer_id": customer_id,
            "note": note
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.SHOPIFY,
            connection_id=connection.nango_connection_id,
            operation=operation,
            parameters=parameters,
            preview=preview
        )
        # Save approval request
        from ..approvals import save_approval_request
        save_approval_request(approval_request)
        return {
            "approval_required": True,
            "approval_request": approval_request.dict()
        }
    
    # Execute directly (should not happen for write ops)
    nango = get_nango_client()
    try:
        draft_order_data = {
            "draft_order": {
                "line_items": line_items
            }
        }
        if customer_id:
            draft_order_data["draft_order"]["customer_id"] = customer_id
        if note:
            draft_order_data["draft_order"]["note"] = note
        
        result = await nango.proxy(
            provider_config_key=Provider.SHOPIFY.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="admin/api/2024-01/draft_orders.json",
            json_data=draft_order_data
        )
        
        log_operation(tenant_id, Provider.SHOPIFY, operation, parameters, result)
        return result.get("draft_order", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.SHOPIFY, operation, parameters, error=str(e))
        raise
