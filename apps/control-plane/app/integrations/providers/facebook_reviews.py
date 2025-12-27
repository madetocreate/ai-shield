"""
Facebook Reviews Integration
Facebook Graph API for Reviews
"""
from typing import Dict, Any, List, Optional
import httpx
from ..nangoClient import get_nango_client


async def read_reviews(tenant_id: str, connection_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read reviews from Facebook."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="facebook-reviews", connection_id=connection_id)
    
    page_id = params.get("page_id") if params else None
    if not page_id:
        return {"error": "page_id required"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://graph.facebook.com/v18.0/{page_id}/ratings",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "fields": "review_text,rating,created_time,reviewer",
                **(params or {})
            }
        )
        if response.status_code != 200:
            return {"error": f"Failed to fetch reviews: {response.status_code}"}
        return response.json()
