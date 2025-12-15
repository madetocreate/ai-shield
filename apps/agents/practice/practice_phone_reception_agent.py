"""
Practice Phone Reception Agent - AI Empfang am Telefon + Chat

Kann:
- Termine buchen/verschieben/stornieren
- Öffnungszeiten/Anfahrt
- "Nehmen Sie Neupatienten?"
- Safety Routing bei medizinischen Inhalten

Inspiration: Doctolib Virtual Phone Assistant, Zocdoc "Zo"
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, date, time


@dataclass
class AppointmentRequest:
    """Terminanfrage"""
    date: date
    time: time
    patient_name: str
    phone: str
    email: Optional[str] = None
    reason: Optional[str] = None  # Minimal, datensparsam!
    is_new_patient: bool = False
    appointment_id: Optional[str] = None


class PracticePhoneReceptionAgent:
    """
    Phone Reception Agent für Praxis-Empfang
    
    Wichtig: Datensparsamkeit (DSGVO), keine medizinischen Diagnosen.
    """
    
    def __init__(self, account_id: str, integration_agent=None, healthcare_privacy_guard=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.healthcare_privacy_guard = healthcare_privacy_guard
        self.practice_info = self._load_practice_info()
    
    def _load_practice_info(self) -> Dict[str, Any]:
        """Lädt Praxis-Informationen"""
        # TODO: Aus Knowledge Base laden
        return {
            "name": "Praxis",
            "address": "",
            "phone": "",
            "opening_hours": {
                "monday": {"open": "08:00", "close": "18:00"},
                "tuesday": {"open": "08:00", "close": "18:00"},
                "wednesday": {"open": "08:00", "close": "18:00"},
                "thursday": {"open": "08:00", "close": "18:00"},
                "friday": {"open": "08:00", "close": "18:00"},
                "saturday": {"open": "09:00", "close": "13:00"},
                "sunday": {"open": None, "close": None},
            },
            "accepts_new_patients": True,
        }
    
    def handle_appointment_request(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Terminanfrage
        
        Wichtig: Minimal nötige Daten sammeln (Datensparsamkeit).
        
        Returns:
            Dict mit Status, Appointment ID, Bestätigung
        """
        # TODO: NLP um Datum, Zeit, Name, Telefon zu extrahieren
        # TODO: Via Healthcare Privacy Guard prüfen
        # TODO: Via Integration Agent Termin buchen (Doctolib/PVS/Calendar)
        
        return {
            "status": "success",
            "message": "Termin erfolgreich vereinbart",
            "appointment_id": None,  # Wird von Integration gesetzt
        }
    
    def check_availability(
        self,
        date: date,
        time: Optional[time] = None
    ) -> Dict[str, Any]:
        """
        Prüft Verfügbarkeit
        
        Returns:
            Dict mit available, alternatives
        """
        # TODO: Via Integration Agent Verfügbarkeit prüfen
        
        return {
            "available": True,
            "alternatives": []
        }
    
    def get_opening_hours(self, day: Optional[str] = None) -> str:
        """Gibt Öffnungszeiten zurück"""
        if day:
            hours = self.practice_info["opening_hours"].get(day.lower())
            if hours and hours.get("open"):
                return f"Am {day} haben wir von {hours['open']} bis {hours['close']} Uhr geöffnet."
            else:
                return f"Am {day} haben wir geschlossen."
        else:
            hours_str = "Unsere Öffnungszeiten:\n"
            for day_name, hours in self.practice_info["opening_hours"].items():
                if hours.get("open"):
                    hours_str += f"{day_name.capitalize()}: {hours['open']} - {hours['close']} Uhr\n"
                else:
                    hours_str += f"{day_name.capitalize()}: Geschlossen\n"
            return hours_str
    
    def handle_safety_routing(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handhabt Safety Routing bei medizinischen Inhalten
        
        Wichtig: Keine Diagnose, nur sichere Standardantworten.
        
        Returns:
            Dict mit action, message, requires_escalation
        """
        # Alarmzeichen prüfen
        alarm_keywords = [
            "atemnot", "brustschmerz", "herz", "bewusstlos",
            "starke schmerzen", "notfall", "112"
        ]
        
        user_lower = user_message.lower()
        has_alarm = any(kw in user_lower for kw in alarm_keywords)
        
        if has_alarm:
            return {
                "action": "emergency",
                "message": "Bei akuten Notfällen wenden Sie sich bitte sofort an den Rettungsdienst unter 112 oder die nächste Notaufnahme.",
                "requires_escalation": True,
                "priority": "critical"
            }
        
        # Standard-Routing
        return {
            "action": "appointment_offer",
            "message": "Ich kann Ihnen gerne einen Termin anbieten, damit Sie Ihre Beschwerden mit unserem Arzt besprechen können. Wann passt es Ihnen?",
            "requires_escalation": False,
            "priority": "normal"
        }
    
    def handle_general_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Beantwortet allgemeine Anfragen"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["öffnungszeit", "wann", "geöffnet"]):
            return self.get_opening_hours()
        
        if any(kw in query_lower for kw in ["adresse", "wo", "finden"]):
            return f"Wir befinden uns unter:\n{self.practice_info['address']}"
        
        if any(kw in query_lower for kw in ["neupatient", "neue patienten", "aufnahme"]):
            if self.practice_info.get("accepts_new_patients"):
                return "Ja, wir nehmen derzeit Neupatienten auf. Gerne können wir einen Termin vereinbaren."
            else:
                return "Derzeit nehmen wir leider keine Neupatienten auf. Bitte versuchen Sie es zu einem späteren Zeitpunkt erneut."
        
        return "Gerne helfe ich Ihnen weiter. Was benötigen Sie?"
