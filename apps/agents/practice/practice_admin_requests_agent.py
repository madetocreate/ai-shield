"""
Practice Admin Requests Agent - Routine-Anliegen, sauber geroutet

Use Cases:
- Rezeptanfrage
- Überweisung
- AU/Attest-Anfrage
- Befundkopie
- Termin zur Befundbesprechung

Wichtig: Kein medizinischer Rat, nur "Anliegen aufnehmen → intern Task → Rückmeldung"

Inspiration: Luma Navigator (Inbound-Call-Agent + Automationen)
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AdminRequestType(str, Enum):
    """Admin-Anfrage-Typen"""
    PRESCRIPTION = "prescription"
    REFERRAL = "referral"
    SICK_NOTE = "sick_note"  # AU
    CERTIFICATE = "certificate"  # Attest
    TEST_RESULT_COPY = "test_result_copy"
    APPOINTMENT_FOR_RESULTS = "appointment_for_results"
    OTHER = "other"


@dataclass
class AdminRequest:
    """Admin-Anfrage"""
    request_id: str
    request_type: AdminRequestType
    patient_name: str
    phone: str
    email: Optional[str] = None
    description: str
    status: str = "pending"  # pending, in_progress, completed, declined
    internal_task_id: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None


class PracticeAdminRequestsAgent:
    """
    Admin Requests Agent für Routine-Anliegen
    
    Wichtig: Keine medizinischen Inhalte, nur Prozess-Management.
    """
    
    def __init__(
        self,
        account_id: str,
        integration_agent=None,
        communications_supervisor=None
    ):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.communications_supervisor = communications_supervisor
        self.requests: List[AdminRequest] = []
    
    def create_request(
        self,
        user_message: str,
        patient_name: str,
        phone: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AdminRequest:
        """
        Erstellt Admin-Anfrage aus User-Nachricht
        
        Returns:
            AdminRequest
        """
        # TODO: NLP um Request-Type zu erkennen
        
        request_type = self._detect_request_type(user_message)
        
        request_id = f"ADM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        request = AdminRequest(
            request_id=request_id,
            request_type=request_type,
            patient_name=patient_name,
            phone=phone,
            description=user_message,
            created_at=datetime.now()
        )
        
        self.requests.append(request)
        
        # TODO: Via Integration Agent internen Task erstellen
        
        return request
    
    def _detect_request_type(self, message: str) -> AdminRequestType:
        """Erkennt Request-Type aus Nachricht"""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ["rezept", "medikament"]):
            return AdminRequestType.PRESCRIPTION
        
        if any(kw in message_lower for kw in ["überweisung", "weisung"]):
            return AdminRequestType.REFERRAL
        
        if any(kw in message_lower for kw in ["au", "krankschreibung", "attest"]):
            return AdminRequestType.SICK_NOTE
        
        if any(kw in message_lower for kw in ["befund", "befundkopie", "labor"]):
            return AdminRequestType.TEST_RESULT_COPY
        
        if any(kw in message_lower for kw in ["besprechung", "ergebnis", "befund besprechen"]):
            return AdminRequestType.APPOINTMENT_FOR_RESULTS
        
        return AdminRequestType.OTHER
    
    def create_internal_task(
        self,
        request: AdminRequest
    ) -> Dict[str, Any]:
        """
        Erstellt internen Task für Team
        
        Returns:
            Dict mit Task ID, Status
        """
        # TODO: Via Integration Agent Task erstellen (z.B. in PVS/Task-System)
        
        task_id = f"TASK-{request.request_id}"
        request.internal_task_id = task_id
        
        return {
            "task_id": task_id,
            "status": "created",
            "message": "Ihr Anliegen wurde an unser Team weitergeleitet."
        }
    
    def update_request_status(
        self,
        request_id: str,
        status: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Aktualisiert Request-Status
        
        Returns:
            Dict mit Status, Next Steps
        """
        request = next((r for r in self.requests if r.request_id == request_id), None)
        
        if not request:
            return {"status": "error", "message": "Anfrage nicht gefunden"}
        
        request.status = status
        
        if status == "completed":
            request.completed_at = datetime.now()
            # TODO: Via Communications Supervisor Rückmeldung an Patient
        
        return {
            "status": status,
            "message": message or f"Anfrage Status: {status}"
        }
    
    def send_status_update(
        self,
        request: AdminRequest,
        update_message: str
    ):
        """Sendet Status-Update an Patient"""
        # TODO: Via Communications Supervisor senden
        pass
    
    def handle_request_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Verarbeitet Admin-Anfrage
        
        Returns:
            Antwort-Text
        """
        # TODO: Request-Type erkennen
        # TODO: Request erstellen
        # TODO: Task erstellen
        
        return "Ihr Anliegen wurde aufgenommen und an unser Team weitergeleitet. Wir melden uns bei Ihnen."
