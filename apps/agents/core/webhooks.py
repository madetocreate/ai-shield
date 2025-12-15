"""
Webhooks & Event System - Webhook System, Event Bus, Notifications

Features:
- Webhook System
- Event Bus
- Event Subscriptions
- Retry Logic für Webhooks
- Event History
"""

from typing import Dict, Optional, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import httpx
import json
import logging
import hashlib

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event Types"""
    AGENT_CALLED = "agent_called"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    ROUTING_DECISION = "routing_decision"
    HANDOFF = "handoff"
    CONSENT_CHECK = "consent_check"
    FEATURE_FLAG_CHANGED = "feature_flag_changed"
    VERSION_DEPLOYED = "version_deployed"
    ALERT_CREATED = "alert_created"
    CUSTOM = "custom"


@dataclass
class Event:
    """Event"""
    id: str
    type: EventType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    account_id: Optional[str] = None


@dataclass
class Webhook:
    """Webhook"""
    id: str
    url: str
    events: List[EventType]  # Events die getriggert werden sollen
    secret: Optional[str] = None  # Für Signatur
    enabled: bool = True
    retry_count: int = 3
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class EventBus:
    """
    Event Bus
    
    Verwaltet Events und sendet sie an Subscriber.
    """
    
    def __init__(self):
        """Initialisiert Event Bus"""
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.webhooks: Dict[str, Webhook] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Abonniert Event"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscriber für {event_type.value} registriert")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Kündigt Event-Abonnement"""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
    
    async def publish(self, event: Event):
        """
        Veröffentlicht Event
        
        Args:
            event: Event
        """
        # Speichere in History
        self.event_history.append(event)
        if len(self.event_history) > 10000:
            self.event_history = self.event_history[-10000:]
        
        # Benachrichtige Subscriber
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Subscriber-Callback Fehler: {e}")
        
        # Trigger Webhooks
        await self._trigger_webhooks(event)
    
    async def _trigger_webhooks(self, event: Event):
        """Triggert Webhooks für Event"""
        for webhook in self.webhooks.values():
            if not webhook.enabled:
                continue
            
            if event.type not in webhook.events:
                continue
            
            await self._send_webhook(webhook, event)
    
    async def _send_webhook(self, webhook: Webhook, event: Event):
        """Sendet Webhook"""
        try:
            payload = {
                "event_id": event.id,
                "event_type": event.type.value,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "account_id": event.account_id
            }
            
            # Signatur hinzufügen (optional)
            if webhook.secret:
                signature = self._generate_signature(payload, webhook.secret)
                headers = {**webhook.headers, "X-Webhook-Signature": signature}
            else:
                headers = webhook.headers
            
            async with httpx.AsyncClient(timeout=webhook.timeout) as client:
                for attempt in range(webhook.retry_count):
                    try:
                        response = await client.post(
                            webhook.url,
                            json=payload,
                            headers=headers
                        )
                        response.raise_for_status()
                        logger.info(f"Webhook {webhook.id} erfolgreich gesendet")
                        return
                    except Exception as e:
                        if attempt < webhook.retry_count - 1:
                            wait_time = 2 ** attempt  # Exponential backoff
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"Webhook {webhook.id} fehlgeschlagen nach {webhook.retry_count} Versuchen: {e}")
        except Exception as e:
            logger.error(f"Fehler beim Senden des Webhooks {webhook.id}: {e}")
    
    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Generiert Webhook-Signatur"""
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(f"{payload_str}{secret}".encode()).hexdigest()
        return signature
    
    def register_webhook(self, webhook: Webhook):
        """Registriert Webhook"""
        self.webhooks[webhook.id] = webhook
        logger.info(f"Webhook {webhook.id} registriert")
    
    def unregister_webhook(self, webhook_id: str):
        """Entfernt Webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Webhook {webhook_id} entfernt")
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Holt Event History"""
        events = self.event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]


# Globale Event Bus-Instanz
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Holt globale Event Bus-Instanz"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus
