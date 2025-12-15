"""
Notion Integration Provider

Notion Pages, Databases, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def pages_list(
    tenant_id: str,
    connection: Connection,
    database_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List Notion pages.
    
    Returns list of pages.
    """
    if connection.status.value != "connected":
        raise ValueError("Notion not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        if database_id:
            # Query database
            result = await nango.proxy(
                provider=Provider.NOTION.value,
                connection_id=connection.nango_connection_id,
                method="POST",
                endpoint=f"v1/databases/{database_id}/query",
                json_data={"page_size": limit}
            )
            log_operation(tenant_id, Provider.NOTION, "pages_list", {"database_id": database_id}, result)
            return result.get("results", [])
        else:
            # List all pages
            result = await nango.proxy(
                provider=Provider.NOTION.value,
                connection_id=connection.nango_connection_id,
                method="GET",
                endpoint="v1/search",
                params={"page_size": limit}
            )
            log_operation(tenant_id, Provider.NOTION, "pages_list", {}, result)
            return result.get("results", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.NOTION, "pages_list", {}, error=str(e))
        raise


async def page_create(
    tenant_id: str,
    connection: Connection,
    parent_id: str,
    title: str,
    content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create Notion page (write operation → requires approval).
    
    Returns approval request if approval required, otherwise created page.
    """
    if connection.status.value != "connected":
        raise ValueError("Notion not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "page_create"
    parameters = {
        "parent_id": parent_id,
        "title": title,
        "content": content
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Create Notion Page",
            "title": title,
            "parent_id": parent_id,
            "has_content": content is not None
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.NOTION,
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
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        
        result = await nango.proxy(
            provider=Provider.NOTION.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="v1/pages",
            json_data=page_data
        )
        
        log_operation(tenant_id, Provider.NOTION, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.NOTION, operation, parameters, error=str(e))
        raise
