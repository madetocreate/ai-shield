"""
iCloud Drive Integration Provider
iCloud Drive Dateien via Nango.
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
    List files from iCloud Drive.
    
    Returns list of files.
    """
    if connection.status.value != "connected":
        raise ValueError("iCloud Drive not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    nango = get_nango_client()
    
    try:
        params = {"limit": limit}
        if folder_id:
            params["folder_id"] = folder_id
        
        result = await nango.proxy(
            provider_config_key=Provider.ICLOUD_DRIVE.value,
            connection_id=connection.nango_connection_id,
            method="GET",
            endpoint="drive/v1/files",
            params=params
        )
        
        log_operation(tenant_id, Provider.ICLOUD_DRIVE, "files_list", params, result)
        return result.get("items", [])
    
    except Exception as e:
        log_operation(tenant_id, Provider.ICLOUD_DRIVE, "files_list", params, error=str(e))
        raise


async def file_upload(
    tenant_id: str,
    connection: Connection,
    file_name: str,
    file_content: bytes,
    folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload file to iCloud Drive (write operation → requires approval).
    """
    if connection.status.value != "connected":
        raise ValueError("iCloud Drive not connected")
    
    if not connection.nango_connection_id:
        raise ValueError("Missing Nango connection ID")
    
    operation = "file_upload"
    parameters = {
        "file_name": file_name,
        "file_size": len(file_content),
        "folder_id": folder_id
    }
    
    if requires_approval(operation):
        preview = {
            "action": "Upload File to iCloud Drive",
            "file_name": file_name,
            "file_size": len(file_content),
            "folder_id": folder_id
        }
        approval_request = create_approval_request(
            tenant_id=tenant_id,
            provider_config_key=Provider.ICLOUD_DRIVE,
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
        # Note: File upload typically requires multipart/form-data
        # This is a simplified version - actual implementation may vary
        result = await nango.proxy(
            provider_config_key=Provider.ICLOUD_DRIVE.value,
            connection_id=connection.nango_connection_id,
            method="POST",
            endpoint="drive/v1/files",
            json_data={
                "name": file_name,
                "folder_id": folder_id,
                "content": file_content.hex()  # Simplified - actual would use proper file upload
            }
        )
        
        log_operation(tenant_id, Provider.ICLOUD_DRIVE, operation, parameters, result)
        return result.get("file", {})
    
    except Exception as e:
        log_operation(tenant_id, Provider.ICLOUD_DRIVE, operation, parameters, error=str(e))
        raise
