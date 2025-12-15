"""
Webhook API Endpoints - FastAPI Endpoints für Webhooks

Endpoints:
- GET /api/v1/webhooks - Liste aller Webhooks
- POST /api/v1/webhooks - Webhook erstellen
- DELETE /api/v1/webhooks/{webhook_id} - Webhook löschen
- GET /api/v1/webhooks/events - Event History
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from apps.agents.core.webhooks import (
    get_event_bus,
    Webhook,
    EventType
)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


# Request Models
class CreateWebhookRequest(BaseModel):
    url: str
    events: List[str]  # Event Types
    secret: Optional[str] = None
    headers: Dict[str, str] = {}
    retry_count: int = 3
    timeout: int = 30


# Response Models
class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    enabled: bool
    created_at: str


@router.get("", response_model=List[WebhookResponse])
def list_webhooks():
    """Listet alle Webhooks"""
    bus = get_event_bus()
    return [
        WebhookResponse(
            id=w.id,
            url=w.url,
            events=[e.value for e in w.events],
            enabled=w.enabled,
            created_at=w.created_at.isoformat()
        )
        for w in bus.webhooks.values()
    ]


@router.post("", response_model=WebhookResponse)
def create_webhook(request: CreateWebhookRequest):
    """Erstellt Webhook"""
    import uuid
    
    bus = get_event_bus()
    
    try:
        events = [EventType(e) for e in request.events]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültiger Event Type: {e}")
    
    webhook = Webhook(
        id=str(uuid.uuid4()),
        url=request.url,
        events=events,
        secret=request.secret,
        headers=request.headers,
        retry_count=request.retry_count,
        timeout=request.timeout
    )
    
    bus.register_webhook(webhook)
    
    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=[e.value for e in webhook.events],
        enabled=webhook.enabled,
        created_at=webhook.created_at.isoformat()
    )


@router.delete("/{webhook_id}")
def delete_webhook(webhook_id: str):
    """Löscht Webhook"""
    bus = get_event_bus()
    bus.unregister_webhook(webhook_id)
    return {"success": True, "message": f"Webhook {webhook_id} gelöscht"}


@router.get("/events")
def get_event_history(
    event_type: Optional[str] = None,
    limit: int = 100
):
    """Holt Event History"""
    bus = get_event_bus()
    
    event_type_enum = None
    if event_type:
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Event Type: {event_type}")
    
    events = bus.get_event_history(event_type_enum, limit=limit)
    
    return {
        "events": [
            {
                "id": e.id,
                "type": e.type.value,
                "payload": e.payload,
                "timestamp": e.timestamp.isoformat(),
                "source": e.source,
                "account_id": e.account_id
            }
            for e in events
        ],
        "count": len(events)
    }
