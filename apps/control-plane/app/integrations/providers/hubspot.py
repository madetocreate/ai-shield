"""
HubSpot Integration Provider

HubSpot CRM, Contacts, Deals, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def contacts_list(
    tenant_id: str,
    connection: Connection,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List HubSpot contacts.
    
    Returns list of contacts.
    """
    if connection.status.value != "connected":
        raise ValueError("HubSpot not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        result = await nango.proxy(
            provider=Provider.HUBSPOT.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="crm/v3/objects/contacts",
            params=params
        )
        
        log_operation(tenant_id, Provider.HUBSPOT, "contacts_list", params, result)
        return result.get("results", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.HUBSPOT, "contacts_list", params, error=str(e))
        raise


async def contact_create(
    tenant_id: str,
    connection: Connection,
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create HubSpot contact (write operation → requires approval).
    
    Returns approval request if approval required, otherwise created contact.
    """
    if connection.status.value != "connected":
        raise ValueError("HubSpot not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "contact_create"
    parameters = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "properties": properties or {}
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Create HubSpot Contact",
            "email": email,
            "name": f"{first_name} {last_name}".strip() if first_name or last_name else email
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.HUBSPOT,
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
        contact_data = {
            "properties": {
                "email": email,
                **(properties or {})
            }
        }
        if first_name:
            contact_data["properties"]["firstname"] = first_name
        if last_name:
            contact_data["properties"]["lastname"] = last_name
        
        result = await nango.proxy(
            provider=Provider.HUBSPOT.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="crm/v3/objects/contacts",
            json_data=contact_data
        )
        
        log_operation(tenant_id, Provider.HUBSPOT, operation, parameters, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.HUBSPOT, operation, parameters, error=str(e))
        raise
