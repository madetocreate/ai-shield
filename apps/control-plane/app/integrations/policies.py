"""
Integration Policies

Read/Write Gating + HITL (Human-in-the-Loop) für Integrationen.
"""
import os
from typing import Dict, Any, Optional
from .types import Provider, ApprovalRequest


WRITE_REQUIRES_APPROVAL = os.environ.get("INTEGRATIONS_WRITE_REQUIRES_APPROVAL", "1") == "1"
AUDIT_LOG_ENABLED = os.environ.get("INTEGRATIONS_AUDIT_LOG", "1") == "1"


def is_write_operation(operation: str) -> bool:
    """
    Check if operation requires write access.
    
    Write operations require approval.
    """
    write_keywords = [
        "create", "update", "set", "write", "send", "post",
        "put", "patch", "delete", "remove", "tag", "modify"
    ]
    operation_lower = operation.lower()
    return any(keyword in operation_lower for keyword in write_keywords)


def requires_approval(operation: str) -> bool:
    """
    Check if operation requires approval.
    
    Currently: all write operations require approval if enabled.
    """
    if not WRITE_REQUIRES_APPROVAL:
        return False
    return is_write_operation(operation)


def get_default_scopes(provider: Provider) -> list[str]:
    """Get default scopes for provider."""
    scope_env_key = f"INTEGRATIONS_DEFAULT_SCOPES_{provider.value.upper()}"
    scopes_str = os.environ.get(scope_env_key, "")
    if scopes_str:
        return [s.strip() for s in scopes_str.split(",") if s.strip()]
    
    # Fallback defaults
    defaults: Dict[Provider, list[str]] = {
        Provider.GOOGLE: ["calendar.readonly"],
        Provider.GOOGLE_DRIVE: ["drive.readonly"],
        Provider.SHOPIFY: ["read_orders", "read_customers"],
        Provider.WOOCOMMERCE: ["read"],
        Provider.HUBSPOT: ["contacts.read"],
        Provider.ZENDESK: ["read"],
        Provider.NOTION: ["read"],
        Provider.SLACK: ["channels:read"],
        Provider.WHATSAPP: ["whatsapp_business_messaging"],
        # Hotel & Booking Platforms
        Provider.BOOKING_COM: ["read"],
        Provider.AIRBNB: ["read"],
        Provider.EXPEDIA: ["read"],
        Provider.HRS: ["read"],
        Provider.HOTELS_COM: ["read"],
        Provider.TRIVAGO: ["read"],
        Provider.AGODA: ["read"],
        Provider.PADEL: ["read"],
        # Real Estate Platforms
        Provider.IMMOBILIENSCOUT24: ["read"],
        Provider.IDEALISTA: ["read"],
        Provider.IMMOWELT: ["read"],
        Provider.EBAY_KLEINANZEIGEN: ["read"],
        Provider.WOHNUNG_DE: ["read"],
        Provider.IMMONET: ["read"],
        Provider.FOTOCASA: ["read"],
        Provider.HABITACLIA: ["read"],
        # Health & Practice Management Platforms
        Provider.MICROSOFT_365: ["Calendars.Read", "Calendars.ReadWrite"],
        Provider.ZOOM: ["meeting:read", "meeting:write"],
        Provider.CALENDLY: ["read"],
        Provider.DOXY_ME: ["read"],
        Provider.SIMPLEPRACTICE: ["read"],
        Provider.JANE_APP: ["read"],
        Provider.EPIC_MYCHART: ["patient.read", "appointment.read"],
        Provider.DOCTOLIB: ["read"],
        # Apple Services
        Provider.APPLE_SIGNIN: ["name", "email"],
        Provider.ICLOUD_CALENDAR: ["calendars.read", "calendars.write"],
        Provider.ICLOUD_DRIVE: ["drive.read", "drive.write"],
        Provider.APPLE_PUSH_NOTIFICATIONS: ["notifications.write"],
        # Review Platforms
        Provider.TRUSTPILOT: ["reviews.read", "reviews.write", "invitations.write"],
        Provider.TRIPADVISOR: ["reviews.read", "reviews.write"],
        Provider.GOOGLE_REVIEWS: ["reviews.read", "reviews.write"],
        Provider.YELP: ["reviews.read"],
        Provider.FACEBOOK_REVIEWS: ["pages_read_engagement", "pages_manage_posts"],
    }
    return defaults.get(provider, [])


def create_approval_request(
    tenant_id: str,
    provider: Provider,
    connection_id: str,
    operation: str,
    parameters: Dict[str, Any],
    preview: Optional[Dict[str, Any]] = None
) -> ApprovalRequest:
    """Create approval request for write operation."""
    import uuid
    from datetime import datetime, timezone
    
    return ApprovalRequest(
        request_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        provider=provider,
        connection_id=connection_id,
        operation=operation,
        parameters=parameters,
        preview=preview,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )


def log_operation(
    tenant_id: str,
    provider: Provider,
    operation: str,
    parameters: Dict[str, Any],
    result: Optional[Any] = None,
    error: Optional[str] = None
):
    """Log operation for audit (if enabled)."""
    if not AUDIT_LOG_ENABLED:
        return
    
    # TODO: Implement proper audit logging
    # For now, just print (in production: use proper logging service)
    import json
    from datetime import datetime, timezone
    log_entry = {
        "tenant_id": tenant_id,
        "provider": provider.value,
        "operation": operation,
        "parameters": parameters,
        "result": str(result) if result else None,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    print(f"[AUDIT] {json.dumps(log_entry)}")
