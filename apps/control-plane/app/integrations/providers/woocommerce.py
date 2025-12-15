"""
WooCommerce Integration Provider

WooCommerce Orders, Customers, etc. via Nango.
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
    Get WooCommerce order status.
    
    Returns list of orders or single order if order_id provided.
    """
    if connection.status.value != "connected":
        raise ValueError("WooCommerce not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        endpoint = f"wp-json/wc/v3/orders/{order_id}" if order_id else "wp-json/wc/v3/orders"
        params = {"per_page": limit} if not order_id else {}
        
        result = await nango.proxy(
            provider=Provider.WOOCOMMERCE.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint=endpoint,
            params=params
        )
        
        log_operation(tenant_id, Provider.WOOCOMMERCE, "orders_get_status", {"order_id": order_id, "limit": limit}, result)
        
        if order_id:
            return result if isinstance(result, dict) else {}
        return result if isinstance(result, list) else []
    
    except Exception as e:
        log_operation(tenant_id, Provider.WOOCOMMERCE, "orders_get_status", {"order_id": order_id}, error=str(e))
        raise


async def customer_tag(
    tenant_id: str,
    connection: Connection,
    customer_id: str,
    tags: List[str]
) -> Dict[str, Any]:
    """
    Tag customer (write operation → requires approval).
    
    Returns approval request if approval required, otherwise updated customer.
    """
    if connection.status.value != "connected":
        raise ValueError("WooCommerce not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "customer_tag"
    parameters = {
        "customer_id": customer_id,
        "tags": tags
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Tag WooCommerce Customer",
            "customer_id": customer_id,
            "tags": tags
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.WOOCOMMERCE,
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
        # First get customer
        customer = await nango.proxy(
            provider=Provider.WOOCOMMERCE.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint=f"wp-json/wc/v3/customers/{customer_id}"
        )
        
        # Update with tags
        existing_tags = customer.get("meta_data", [])
        existing_tag_values = [t.get("value", "") for t in existing_tags if t.get("key") == "tags"]
        all_tags = list(set(existing_tag_values + tags))
        
        update_data = {
            "meta_data": existing_tags + [{"key": "tags", "value": ",".join(all_tags)}]
        }
        
        result = await nango.proxy(
            provider=Provider.WOOCOMMERCE.value,
            connection_id=connection.nango_connection_id,
            method="PUT",
            endpoint=f"wp-json/wc/v3/customers/{customer_id}",
            json_data=update_data
        )
        
        log_operation(tenant_id, Provider.WOOCOMMERCE, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.WOOCOMMERCE, operation, parameters, error=str(e))
        raise
