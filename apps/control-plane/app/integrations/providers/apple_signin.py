"""
Apple Sign In Integration Provider
Apple ID Authentication via OAuth 2.0.
"""
from typing import Dict, Any, Optional
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def user_info(
    tenant_id: str,
    connection: Connection
) -> Dict[str, Any]:
    """
    Get user information from Apple ID.
    
    Returns user profile information.
    """
    if connection.status.value != "connected":
        raise ValueError("Apple Sign In not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        result = await nango.proxy(
            provider=Provider.APPLE_SIGNIN.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="v1/userinfo",
            params={}
        )
        
        log_operation(tenant_id, Provider.APPLE_SIGNIN, "user_info", {}, result)
        return result
    
    except Exception as e:
        log_operation(tenant_id, Provider.APPLE_SIGNIN, "user_info", {}, error=str(e))
        raise
