"""
Google Reviews Integration
Google My Business API for Reviews
"""
from typing import Dict, Any, List, Optional
import httpx
from ..nangoClient import get_nango_client


async def read_reviews(tenant_id: str, connection_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read reviews from Google My Business."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="google-reviews", connection_id=connection_id)
    
    location_id = params.get("location_id") if params else None
    if not location_id:
        return {"error": "location_id required"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://mybusiness.googleapis.com/v4/locations/{location_id}/reviews",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params or {}
        )
        if response.status_code != 200:
            return {"error": f"Failed to fetch reviews: {response.status_code}"}
        return response.json()


async def respond_to_review(tenant_id: str, connection_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Respond to a review on Google My Business."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="google-reviews", connection_id=connection_id)
    
    review_id = params.get("review_id")
    location_id = params.get("location_id")
    if not review_id or not location_id:
        return {"error": "review_id and location_id required"}
    
    response_data = {
        "comment": params.get("message"),
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://mybusiness.googleapis.com/v4/locations/{location_id}/reviews/{review_id}/reply",
            headers={"Authorization": f"Bearer {access_token}"},
            json=response_data
        )
        if response.status_code not in [200, 201]:
            return {"error": f"Failed to respond to review: {response.status_code}"}
        return response.json()
