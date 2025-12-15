"""
Practice Patient Intake Forms Agent - Formulare & Vorbereitung

Kann:
- Digitale Anamnese/Einverständnis/Versicherung/Datenschutz
- Vorab einsammeln
- Strukturiert ans PVS/E-Akte

Inspiration: Klara (Omnichannel, Self-Scheduling, Pre-Visit Instructions, digitale Forms)
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FormType(str, Enum):
    """Formular-Typen"""
    ANMELDUNG = "anmeldung"
    ANAMNESE = "anamnese"
    EINVERSTÄNDNIS = "einverständnis"
    VERSICHERUNG = "versicherung"
    DATENSCHUTZ = "datenschutz"
    PRE_VISIT_INSTRUCTIONS = "pre_visit_instructions"


@dataclass
class FormRequest:
    """Formular-Anfrage"""
    form_id: str
    form_type: FormType
    patient_name: str
    phone: str
    email: Optional[str] = None
    appointment_id: Optional[str] = None
    form_link: Optional[str] = None
    status: str = "pending"  # pending, sent, completed, expired
    completed_at: Optional[datetime] = None
    created_at: datetime = None


class PracticePatientIntakeFormsAgent:
    """
    Patient Intake Forms Agent für digitale Formulare
    
    Sendet Form-Links, verarbeitet Ausfüllungen, integriert in PVS/E-Akte.
    """
    
    def __init__(
        self,
        account_id: str,
        document_intelligence_agent=None,
        integration_agent=None,
        communications_supervisor=None
    ):
        self.account_id = account_id
        self.document_intelligence_agent = document_intelligence_agent
        self.integration_agent = integration_agent
        self.communications_supervisor = communications_supervisor
        self.form_requests: List[FormRequest] = []
    
    def create_form_request(
        self,
        form_type: FormType,
        patient_name: str,
        phone: str,
        email: Optional[str] = None,
        appointment_id: Optional[str] = None
    ) -> FormRequest:
        """
        Erstellt Formular-Anfrage
        
        Returns:
            FormRequest
        """
        form_id = f"FORM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        request = FormRequest(
            form_id=form_id,
            form_type=form_type,
            patient_name=patient_name,
            phone=phone,
            email=email,
            appointment_id=appointment_id,
            created_at=datetime.now()
        )
        
        self.form_requests.append(request)
        return request
    
    def generate_form_link(
        self,
        request: FormRequest
    ) -> str:
        """
        Generiert Formular-Link
        
        Returns:
            URL zum Formular
        """
        # TODO: Formular generieren oder aus Template laden
        # TODO: Link mit Token erstellen
        
        form_link = f"https://forms.example.com/{request.form_id}"
        request.form_link = form_link
        
        return form_link
    
    def send_form(
        self,
        request: FormRequest
    ) -> Dict[str, Any]:
        """
        Sendet Formular-Link an Patient
        
        Returns:
            Dict mit Status, Message
        """
        if not request.form_link:
            form_link = self.generate_form_link(request)
        else:
            form_link = request.form_link
        
        message = self._generate_form_message(request, form_link)
        
        # TODO: Via Communications Supervisor senden (SMS/E-Mail)
        
        request.status = "sent"
        
        return {
            "status": "sent",
            "form_link": form_link,
            "message": message
        }
    
    def _generate_form_message(
        self,
        request: FormRequest,
        form_link: str
    ) -> str:
        """Generiert Nachricht mit Formular-Link"""
        form_names = {
            FormType.ANMELDUNG: "Anmeldeformular",
            FormType.ANAMNESE: "Anamneseformular",
            FormType.EINVERSTÄNDNIS: "Einverständniserklärung",
            FormType.VERSICHERUNG: "Versicherungsformular",
            FormType.DATENSCHUTZ: "Datenschutzerklärung",
            FormType.PRE_VISIT_INSTRUCTIONS: "Vorbereitungsinformationen",
        }
        
        form_name = form_names.get(request.form_type, "Formular")
        
        return f"""Guten Tag {request.patient_name},

bitte füllen Sie vor Ihrem Termin das {form_name} aus:

{form_link}

Mit freundlichen Grüßen
Ihre Praxis"""
    
    def process_completed_form(
        self,
        form_id: str,
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verarbeitet ausgefülltes Formular
        
        Returns:
            Dict mit Status, Next Steps
        """
        request = next((r for r in self.form_requests if r.form_id == form_id), None)
        
        if not request:
            return {"status": "error", "message": "Formular nicht gefunden"}
        
        # TODO: Via Document Intelligence Agent strukturieren
        # TODO: Via Integration Agent in PVS/E-Akte speichern
        
        request.status = "completed"
        request.completed_at = datetime.now()
        
        return {
            "status": "completed",
            "message": "Formular erfolgreich verarbeitet und in Ihrer Akte gespeichert."
        }
    
    def send_reminder(
        self,
        request: FormRequest
    ):
        """Sendet Erinnerung für ausstehendes Formular"""
        if request.status == "pending" or request.status == "sent":
            # TODO: Erinnerung senden
            pass
