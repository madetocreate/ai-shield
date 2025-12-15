"""
Restaurant Events Catering Agent - Gruppen/Events/Catering → Deal

Kann:
- "20 Personen am Samstag", "Catering für Firma", "Private Dining"
- Requirements aufnehmen, Budget grob abfragen
- Angebot/Proposal erzeugen
- Follow-up-Sequenz starten

Baut auf CRM/Proposal/Follow-up Agents auf.
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from enum import Enum


class EventType(str, Enum):
    """Event-Typen"""
    PRIVATE_DINING = "private_dining"
    CORPORATE_EVENT = "corporate_event"
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    CATERING = "catering"
    OTHER = "other"


@dataclass
class EventRequest:
    """Event-Anfrage"""
    event_id: str
    event_type: EventType
    date: date
    time: Optional[time] = None
    guests: int
    contact_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    company: Optional[str] = None
    budget_range: Optional[str] = None  # z.B. "1000-2000€"
    special_requirements: Optional[str] = None
    dietary_requirements: Optional[List[str]] = None
    status: str = "inquiry"  # inquiry, proposal_sent, confirmed, declined
    created_at: datetime = None


class RestaurantEventsCateringAgent:
    """
    Events & Catering Agent für Gruppenbuchungen
    
    Sammelt Requirements, erstellt Proposals, startet Follow-ups.
    """
    
    def __init__(
        self,
        account_id: str,
        crm_agent=None,
        proposal_agent=None,
        followup_agent=None,
        personalization_agent=None
    ):
        self.account_id = account_id
        self.crm_agent = crm_agent
        self.proposal_agent = proposal_agent
        self.followup_agent = followup_agent
        self.personalization_agent = personalization_agent
        self.event_requests: List[EventRequest] = []
    
    def create_event_request(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> EventRequest:
        """
        Erstellt Event-Anfrage aus User-Nachricht
        
        Returns:
            EventRequest
        """
        # TODO: NLP um Event-Details zu extrahieren
        # TODO: Event-Type erkennen
        
        event_id = f"EVT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        request = EventRequest(
            event_id=event_id,
            event_type=EventType.OTHER,  # TODO: Erkennen
            date=date.today(),  # TODO: Extrahieren
            guests=10,  # TODO: Extrahieren
            contact_name="",  # TODO: Extrahieren
            contact_phone="",  # TODO: Extrahieren
            created_at=datetime.now()
        )
        
        self.event_requests.append(request)
        return request
    
    def collect_requirements(
        self,
        request: EventRequest,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Sammelt weitere Requirements
        
        Returns:
            Dict mit fehlenden/gesammelten Infos
        """
        missing = []
        
        if not request.date:
            missing.append("Datum")
        if not request.time:
            missing.append("Uhrzeit")
        if request.guests == 0:
            missing.append("Anzahl Gäste")
        if not request.contact_name:
            missing.append("Ihr Name")
        if not request.contact_phone:
            missing.append("Telefonnummer")
        if not request.contact_email:
            missing.append("E-Mail-Adresse")
        
        # TODO: NLP um fehlende Infos aus user_message zu extrahieren
        
        return {
            "missing_info": missing,
            "complete": len(missing) == 0
        }
    
    def create_proposal(
        self,
        request: EventRequest
    ) -> Dict[str, Any]:
        """
        Erstellt Angebot/Proposal
        
        Returns:
            Dict mit Proposal-Details
        """
        # TODO: Via Proposal Agent Angebot erstellen
        # TODO: Preise basierend auf Gästezahl, Event-Type, etc.
        
        proposal = {
            "proposal_id": f"PROP-{request.event_id}",
            "event_request_id": request.event_id,
            "total_price": 0.0,  # TODO: Berechnen
            "items": [],  # TODO: Menü, Getränke, Service, etc.
            "valid_until": (datetime.now() + timedelta(days=7)).isoformat(),
        }
        
        request.status = "proposal_sent"
        
        return proposal
    
    def start_followup_sequence(
        self,
        request: EventRequest
    ):
        """Startet Follow-up-Sequenz"""
        # TODO: Via Followup Agent Sequence starten
        # TODO: Personalisierung via Personalization Agent
        pass
    
    def handle_event_inquiry(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Verarbeitet Event-Anfrage
        
        Returns:
            Antwort-Text
        """
        # TODO: Event-Type erkennen
        # TODO: Requirements sammeln
        # TODO: CRM Deal erstellen via CRM Agent
        
        return "Gerne helfen wir Ihnen bei Ihrer Veranstaltung. Wann soll das Event stattfinden und für wie viele Gäste planen Sie?"
