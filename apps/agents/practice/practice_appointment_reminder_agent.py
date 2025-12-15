"""
Practice Appointment Reminder Agent - No-Show-Killer

Kann:
- Bestätigen/Absagen/Umplanen per SMS/E-Mail
- Erinnerungslogik
- Warteliste

Inspiration: NexHealth Trigger/Journeys (Confirmed, Reminders, Missed, Cancelled, Recalls)
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class ReminderStatus(str, Enum):
    """Reminder-Status"""
    PENDING = "pending"
    SENT = "sent"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    MISSED = "missed"


@dataclass
class AppointmentReminder:
    """Terminerinnerung"""
    reminder_id: str
    appointment_id: str
    patient_name: str
    phone: str
    email: Optional[str] = None
    appointment_date: datetime = None
    reminder_sent_at: Optional[datetime] = None
    status: ReminderStatus = ReminderStatus.PENDING
    channel: str = "sms"  # sms, email, both


class PracticeAppointmentReminderAgent:
    """
    Appointment Reminder Agent für No-Show-Reduktion
    
    Sendet Erinnerungen, verarbeitet Bestätigungen/Absagen, verwaltet Warteliste.
    """
    
    def __init__(self, account_id: str, integration_agent=None, communications_supervisor=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.communications_supervisor = communications_supervisor
        self.reminders: List[AppointmentReminder] = []
        self.waitlist: List[Dict[str, Any]] = []
    
    def schedule_reminder(
        self,
        appointment_id: str,
        appointment_date: datetime,
        patient_name: str,
        phone: str,
        email: Optional[str] = None,
        days_before: int = 1
    ) -> AppointmentReminder:
        """
        Plant Erinnerung für Termin
        
        Args:
            days_before: Wie viele Tage vorher erinnern
        
        Returns:
            AppointmentReminder
        """
        reminder_id = f"REM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        reminder = AppointmentReminder(
            reminder_id=reminder_id,
            appointment_id=appointment_id,
            patient_name=patient_name,
            phone=phone,
            email=email,
            appointment_date=appointment_date,
            status=ReminderStatus.PENDING
        )
        
        self.reminders.append(reminder)
        
        # TODO: Via Integration Agent Reminder in System eintragen
        
        return reminder
    
    def send_reminder(
        self,
        reminder: AppointmentReminder
    ) -> Dict[str, Any]:
        """
        Sendet Erinnerung
        
        Returns:
            Dict mit Status, Message
        """
        message = self._generate_reminder_message(reminder)
        
        # TODO: Via Communications Supervisor senden (SMS/E-Mail)
        
        reminder.reminder_sent_at = datetime.now()
        reminder.status = ReminderStatus.SENT
        
        return {
            "status": "sent",
            "message": message,
            "reminder_id": reminder.reminder_id
        }
    
    def _generate_reminder_message(self, reminder: AppointmentReminder) -> str:
        """Generiert Erinnerungsnachricht"""
        date_str = reminder.appointment_date.strftime("%d.%m.%Y")
        time_str = reminder.appointment_date.strftime("%H:%M")
        
        return f"""Guten Tag {reminder.patient_name},

dies ist eine Erinnerung an Ihren Termin am {date_str} um {time_str} Uhr.

Bitte bestätigen Sie mit JA, absagen mit NEIN, oder verschieben mit VERSCHIEBEN.

Mit freundlichen Grüßen
Ihre Praxis"""
    
    def process_confirmation(
        self,
        reminder_id: str,
        response: str
    ) -> Dict[str, Any]:
        """
        Verarbeitet Bestätigung/Absage/Umplanung
        
        Args:
            response: "JA", "NEIN", "VERSCHIEBEN"
        
        Returns:
            Dict mit Status, Action
        """
        reminder = next((r for r in self.reminders if r.reminder_id == reminder_id), None)
        
        if not reminder:
            return {"status": "error", "message": "Reminder nicht gefunden"}
        
        response_upper = response.upper().strip()
        
        if response_upper in ["JA", "JA", "BESTÄTIGEN", "OK"]:
            reminder.status = ReminderStatus.CONFIRMED
            return {
                "status": "confirmed",
                "message": "Termin bestätigt. Wir freuen uns auf Ihren Besuch."
            }
        
        elif response_upper in ["NEIN", "ABSAGEN", "STORNIEREN"]:
            reminder.status = ReminderStatus.CANCELLED
            # TODO: Via Integration Agent Termin stornieren
            # TODO: Warteliste prüfen und nächsten Patient informieren
            return {
                "status": "cancelled",
                "message": "Termin storniert. Möchten Sie einen neuen Termin vereinbaren?"
            }
        
        elif response_upper in ["VERSCHIEBEN", "UMPLANEN"]:
            reminder.status = ReminderStatus.RESCHEDULED
            return {
                "status": "rescheduled",
                "message": "Bitte nennen Sie uns Ihren Wunschtermin."
            }
        
        return {"status": "unknown", "message": "Bitte antworten Sie mit JA, NEIN oder VERSCHIEBEN."}
    
    def handle_missed_appointment(
        self,
        appointment_id: str
    ):
        """Handhabt verpassten Termin"""
        reminder = next(
            (r for r in self.reminders if r.appointment_id == appointment_id),
            None
        )
        
        if reminder:
            reminder.status = ReminderStatus.MISSED
        
        # TODO: Recall-Strategie (Warteliste, Follow-up)
    
    def add_to_waitlist(
        self,
        patient_name: str,
        phone: str,
        preferred_dates: List[datetime]
    ) -> Dict[str, Any]:
        """Fügt Patient zur Warteliste hinzu"""
        waitlist_entry = {
            "patient_name": patient_name,
            "phone": phone,
            "preferred_dates": preferred_dates,
            "added_at": datetime.now()
        }
        
        self.waitlist.append(waitlist_entry)
        
        return {
            "status": "added",
            "message": "Sie wurden zur Warteliste hinzugefügt. Wir melden uns bei Verfügbarkeit."
        }
