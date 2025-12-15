"""
Google Drive Integration Provider

Google Drive Files, Documents, etc. via Nango.
"""
from typing import Dict, Any, Optional, List
from ..types import Provider, Connection
from ..nangoClient import get_nango_client
from ..policies import requires_approval, create_approval_request, log_operation


async def files_list(
    tenant_id: str,
    connection: Connection,
    folder_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List files in Google Drive.
    
    Returns list of files.
    """
    if connection.status.value != "connected":
        raise ValueError("Google Drive not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {
            "pageSize": limit,
            "fields": "files(id,name,mimeType,modifiedTime,size)"
        }
        if folder_id:
            params["q"] = f"'{folder_id}' in parents"
        
        result = await nango.proxy(
            provider=Provider.GOOGLE_DRIVE.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="drive/v3/files",
            params=params
        )
        
        log_operation(tenant_id, Provider.GOOGLE_DRIVE, "files_list", params, result)
        return result.get("files", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.GOOGLE_DRIVE, "files_list", params, error=str(e))
        raise


async def file_upload(
    tenant_id: str,
    connection: Connection,
    name: str,
    content: bytes,
    folder_id: Optional[str] = None,
    mime_type: str = "text/plain"
) -> Dict[str, Any]:
    """
    Upload file to Google Drive (write operation → requires approval).
    
    Returns approval request if approval required, otherwise uploaded file info.
    """
    if connection.status.value != "connected":
        raise ValueError("Google Drive not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "file_upload"
    parameters = {
        "name": name,
        "folder_id": folder_id,
        "mime_type": mime_type,
        "size": len(content)
    }
    
    # Check if approval required
    if requires_approval(operation):
        preview = {
            "action": "Upload File to Google Drive",
            "name": name,
            "size": len(content),
            "folder_id": folder_id or "root"
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider=Provider.GOOGLE_DRIVE,
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
        # TODO: Implement actual file upload via Nango
        log_operation(tenant_id, Provider.GOOGLE_DRIVE, operation, parameters, {"file_id": "stub"})
        return {"file_id": "stub", "name": name}
    
    except Exception as e:
        log_operation(tenant_id, Provider.GOOGLE_DRIVE, operation, parameters, error=str(e))
        raise
