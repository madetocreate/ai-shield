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
    # Use provider.name (ENV-safe) instead of provider.value.upper()
    # provider.name is like "GOOGLE", "GOOGLE_DRIVE", "MICROSOFT_365"
    scope_env_key = f"INTEGRATIONS_DEFAULT_SCOPES_{provider.name}"
    scopes_str = os.environ.get(scope_env_key, "")
    if scopes_str:
        # Parse JSON array or comma-separated string
        try:
            import json
            parsed = json.loads(scopes_str)
            if isinstance(parsed, list):
                return [str(s).strip() for s in parsed if s]
        except (json.JSONDecodeError, ValueError):
            pass
        # Fallback: comma-separated string
        scopes = [s.strip() for s in scopes_str.split(",") if s.strip()]
        # Dedupe
        seen = set()
        result = []
        for s in scopes:
            if s not in seen:
                seen.add(s)
                result.append(s)
        if result:
            return result
    
    # Fallback defaults (only for providers that exist in Enum)
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
        # Booking Platforms
        Provider.PADEL: ["read"],
        # Calendar & Meeting Platforms
        Provider.CALENDLY: ["read"],
        Provider.MICROSOFT_365: ["Calendars.Read", "Calendars.ReadWrite"],
        Provider.ZOOM: ["meeting:read", "meeting:write"],
        # Apple Services
        Provider.APPLE_SIGNIN: ["name", "email"],
        Provider.ICLOUD_CALENDAR: ["calendars.read", "calendars.write"],
        Provider.ICLOUD_DRIVE: ["drive.read", "drive.write"],
        Provider.APPLE_PUSH_NOTIFICATIONS: ["notifications.write"],
        # Review Platforms
        Provider.TRUSTPILOT: ["reviews.read", "reviews.write", "invitations.write"],
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


def _redact_value(value: Any) -> Any:
    """Recursively redact sensitive values from objects."""
    if isinstance(value, str):
        # Redact strings matching token/secret patterns
        import re
        # Redact API keys (sk-, pk-, etc.)
        if re.search(r'\b(sk|pk|ak|tk)-[a-zA-Z0-9]{20,}', value, re.IGNORECASE):
            return "<REDACTED_API_KEY>"
        # Redact bearer tokens
        if re.search(r'\bbearer\s+[a-zA-Z0-9_-]{20,}', value, re.IGNORECASE):
            return "<REDACTED_TOKEN>"
        return value
    elif isinstance(value, dict):
        return {k: _redact_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_redact_value(item) for item in value]
    else:
        return value


def _redact_dict(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive keys from dictionary."""
    import re
    redacted = {}
    sensitive_pattern = re.compile(
        r'(token|secret|authorization|api[_-]?key|password|credential|auth)',
        re.IGNORECASE
    )
    
    for key, value in obj.items():
        if sensitive_pattern.search(key):
            redacted[key] = "<REDACTED>"
        else:
            redacted[key] = _redact_value(value)
    
    return redacted


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
    
    # Redact sensitive data before logging
    import json
    from datetime import datetime, timezone
    
    # Redact parameters
    redacted_params = _redact_dict(parameters) if isinstance(parameters, dict) else parameters
    
    # Redact result (if dict)
    redacted_result = None
    if result:
        if isinstance(result, dict):
            redacted_result = _redact_dict(result)
        elif isinstance(result, str):
            redacted_result = _redact_value(result)
        else:
            redacted_result = str(result)
    
    log_entry = {
        "tenant_id": tenant_id,
        "provider": provider.value,
        "operation": operation,
        "parameters": redacted_params,
        "result": redacted_result,
        "error": error,  # Errors are usually safe to log
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Use proper logging instead of print
    import logging
    logger = logging.getLogger("integrations.audit")
    logger.info(f"[AUDIT] {json.dumps(log_entry)}")
