"""
Yelp Integration
Yelp Fusion API for Reviews
"""
from typing import Dict, Any, List, Optional
import httpx
from ..nangoClient import get_nango_client


async def read_reviews(tenant_id: str, connection_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read reviews from Yelp."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(tenant_id, "yelp", connection_id)
    
    business_id = params.get("business_id") if params else None
    if not business_id:
        return {"error": "business_id required"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.yelp.com/v3/businesses/{business_id}/reviews",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params or {}
        )
        if response.status_code != 200:
            return {"error": f"Failed to fetch reviews: {response.status_code}"}
        return response.json()
