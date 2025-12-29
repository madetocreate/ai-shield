"""
Trustpilot Integration
Review Management and Invitation API
"""
from typing import Dict, Any, List, Optional
import httpx
from ..nangoClient import get_nango_client


async def read_reviews(tenant_id: str, connection_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read reviews from Trustpilot."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="trustpilot", connection_id=connection_id)
    
    business_unit_id = params.get("business_unit_id") if params else None
    if not business_unit_id:
        return {"error": "business_unit_id required"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trustpilot.com/v1/business-units/{business_unit_id}/reviews",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params or {}
        )
        if response.status_code != 200:
            return {"error": f"Failed to fetch reviews: {response.status_code}"}
        return response.json()


async def create_invitation(tenant_id: str, connection_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Create review invitation via Trustpilot."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="trustpilot", connection_id=connection_id)
    
    business_unit_id = params.get("business_unit_id")
    if not business_unit_id:
        return {"error": "business_unit_id required"}
    
    invitation_data = {
        "recipientEmail": params.get("recipient_email"),
        "recipientName": params.get("recipient_name"),
        "referenceNumber": params.get("reference_number"),
        "locale": params.get("locale", "de-DE"),
        "templateId": params.get("template_id"),
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://invitations-api.trustpilot.com/v1/private/business-units/{business_unit_id}/email-invitations",
            headers={"Authorization": f"Bearer {access_token}"},
            json=invitation_data
        )
        if response.status_code not in [200, 201]:
            return {"error": f"Failed to create invitation: {response.status_code}"}
        return response.json()


async def respond_to_review(tenant_id: str, connection_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Respond to a review on Trustpilot."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="trustpilot", connection_id=connection_id)
    
    review_id = params.get("review_id")
    if not review_id:
        return {"error": "review_id required"}
    
    response_data = {
        "message": params.get("message"),
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.trustpilot.com/v1/private/reviews/{review_id}/reply",
            headers={"Authorization": f"Bearer {access_token}"},
            json=response_data
        )
        if response.status_code not in [200, 201]:
            return {"error": f"Failed to respond to review: {response.status_code}"}
        return response.json()


async def get_business_units(tenant_id: str, connection_id: str) -> Dict[str, Any]:
    """Get business units for the authenticated user."""
    nango = get_nango_client()
    access_token = await nango.get_access_token(provider_config_key="trustpilot", connection_id=connection_id)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.trustpilot.com/v1/business-units",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            return {"error": f"Failed to fetch business units: {response.status_code}"}
        return response.json()
