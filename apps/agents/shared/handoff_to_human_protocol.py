"""
Handoff to Human Protocol - Einheitlicher Eskalationsstandard

Definiert wann und wie von AI zu Human übergeben wird.
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class HandoffReason(str, Enum):
    """Gründe für Human Handoff"""
    COMPLEX_QUERY = "complex_query"
    EMOTIONAL_DISTRESS = "emotional_distress"
    SAFETY_CONCERN = "safety_concern"
    POLICY_VIOLATION = "policy_violation"
    TECHNICAL_ISSUE = "technical_issue"
    USER_REQUEST = "user_request"
    ESCALATION_REQUIRED = "escalation_required"
    CONSENT_REQUIRED = "consent_required"


class HandoffPriority(str, Enum):
    """Priorität des Handoffs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class HandoffMethod(str, Enum):
    """Methode der Übergabe"""
    LIVE_TRANSFER = "live_transfer"  # Sofortige Live-Übergabe (z.B. Telefon)
    TICKET = "ticket"  # Ticket-System
    CALLBACK = "callback"  # Rückruf anfordern
    SCHEDULED = "scheduled"  # Termin vereinbaren
    EMAIL = "email"  # E-Mail an Team


@dataclass
class HandoffContext:
    """Kontext für Human Handoff"""
    account_id: str
    user_id: Optional[str]
    channel: str  # phone, chat, email, sms
    conversation_id: str
    reason: HandoffReason
    priority: HandoffPriority
    method: HandoffMethod
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HandoffRule:
    """Regel für automatischen Handoff"""
    reason: HandoffReason
    priority: HandoffPriority
    method: HandoffMethod
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class HandoffToHumanProtocol:
    """
    Protokoll für Human Handoffs
    
    Entscheidet wann und wie übergeben wird.
    """
    
    def __init__(self):
        self.rules: List[HandoffRule] = self._default_rules()
        self.handoffs: List[HandoffContext] = []
    
    def _default_rules(self) -> List[HandoffRule]:
        """Standard Handoff-Regeln"""
        return [
            HandoffRule(
                reason=HandoffReason.SAFETY_CONCERN,
                priority=HandoffPriority.CRITICAL,
                method=HandoffMethod.LIVE_TRANSFER
            ),
            HandoffRule(
                reason=HandoffReason.EMOTIONAL_DISTRESS,
                priority=HandoffPriority.HIGH,
                method=HandoffMethod.LIVE_TRANSFER
            ),
            HandoffRule(
                reason=HandoffReason.USER_REQUEST,
                priority=HandoffPriority.MEDIUM,
                method=HandoffMethod.LIVE_TRANSFER
            ),
            HandoffRule(
                reason=HandoffReason.COMPLEX_QUERY,
                priority=HandoffPriority.LOW,
                method=HandoffMethod.TICKET
            ),
            HandoffRule(
                reason=HandoffReason.CONSENT_REQUIRED,
                priority=HandoffPriority.MEDIUM,
                method=HandoffMethod.CALLBACK
            ),
        ]
    
    def should_handoff(
        self,
        account_id: str,
        user_id: Optional[str],
        channel: str,
        conversation_id: str,
        reason: HandoffReason,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[HandoffContext]:
        """
        Entscheidet ob Handoff nötig ist und erstellt Handoff-Context
        
        Returns:
            HandoffContext wenn Handoff nötig, sonst None
        """
        # Finde passende Regel
        rule = None
        for r in self.rules:
            if r.reason == reason and r.enabled:
                rule = r
                break
        
        if not rule:
            return None
        
        # Erstelle Handoff-Context
        summary = self._generate_summary(reason, context or {})
        
        handoff = HandoffContext(
            account_id=account_id,
            user_id=user_id,
            channel=channel,
            conversation_id=conversation_id,
            reason=reason,
            priority=rule.priority,
            method=rule.method,
            summary=summary,
            metadata=context or {}
        )
        
        self.handoffs.append(handoff)
        return handoff
    
    def _generate_summary(self, reason: HandoffReason, context: Dict[str, Any]) -> str:
        """Generiert Zusammenfassung für Handoff"""
        summaries = {
            HandoffReason.SAFETY_CONCERN: "Sicherheitsbedenken erkannt - sofortige Eskalation erforderlich",
            HandoffReason.EMOTIONAL_DISTRESS: "Emotionale Belastung erkannt - menschliche Unterstützung benötigt",
            HandoffReason.USER_REQUEST: "Benutzer hat explizit nach menschlichem Support gefragt",
            HandoffReason.COMPLEX_QUERY: "Komplexe Anfrage erfordert menschliche Expertise",
            HandoffReason.POLICY_VIOLATION: "Policy-Verletzung erkannt - Überprüfung erforderlich",
            HandoffReason.TECHNICAL_ISSUE: "Technisches Problem - Support benötigt",
            HandoffReason.ESCALATION_REQUIRED: "Eskalation erforderlich basierend auf Kontext",
            HandoffReason.CONSENT_REQUIRED: "Consent-Management erforderlich",
        }
        
        base_summary = summaries.get(reason, "Handoff erforderlich")
        
        if context:
            details = ", ".join([f"{k}: {v}" for k, v in context.items() if v])
            if details:
                return f"{base_summary} - {details}"
        
        return base_summary
    
    def get_pending_handoffs(
        self,
        account_id: Optional[str] = None,
        priority: Optional[HandoffPriority] = None
    ) -> List[HandoffContext]:
        """Holt ausstehende Handoffs"""
        filtered = self.handoffs
        
        if account_id:
            filtered = [h for h in filtered if h.account_id == account_id]
        
        if priority:
            filtered = [h for h in filtered if h.priority == priority]
        
        # Sortiere nach Priorität und Zeit
        priority_order = {
            HandoffPriority.CRITICAL: 0,
            HandoffPriority.URGENT: 1,
            HandoffPriority.HIGH: 2,
            HandoffPriority.MEDIUM: 3,
            HandoffPriority.LOW: 4
        }
        
        filtered.sort(key=lambda h: (priority_order.get(h.priority, 99), h.created_at))
        return filtered
    
    def add_rule(self, rule: HandoffRule):
        """Fügt Handoff-Regel hinzu"""
        self.rules.append(rule)
    
    def update_rule(self, reason: HandoffReason, **updates):
        """Aktualisiert Handoff-Regel"""
        for rule in self.rules:
            if rule.reason == reason:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                break


# Globale Protocol-Instanz
_global_protocol: Optional[HandoffToHumanProtocol] = None


def get_protocol() -> HandoffToHumanProtocol:
    """Holt globale Protocol-Instanz"""
    global _global_protocol
    if _global_protocol is None:
        _global_protocol = HandoffToHumanProtocol()
    return _global_protocol
