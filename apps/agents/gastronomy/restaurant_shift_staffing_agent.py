"""
Restaurant Shift Staffing Agent - Schicht & Ausfälle

Kann:
- "Ich bin krank" → Ersatz anfragen
- Schichtplan aktualisieren
- Team informieren

V2 Add-on für Gastronomie-Paket
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, date, time
from enum import Enum


class ShiftStatus(str, Enum):
    """Schicht-Status"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COVERED = "covered"
    UNCOVERED = "uncovered"


@dataclass
class Shift:
    """Schicht"""
    shift_id: str
    staff_member: str
    date: date
    start_time: time
    end_time: time
    role: str  # Kellner, Koch, etc.
    status: ShiftStatus = ShiftStatus.SCHEDULED
    replacement_needed: bool = False


class RestaurantShiftStaffingAgent:
    """
    Shift Staffing Agent für Schichtplanung und Ausfälle
    
    V2 Add-on für Gastronomie-Paket
    """
    
    def __init__(self, account_id: str, integration_agent=None, communications_supervisor=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.communications_supervisor = communications_supervisor
        self.shifts: List[Shift] = []
    
    def handle_absence_request(
        self,
        staff_member: str,
        date: date,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Abwesenheits-Anfrage
        
        Args:
            staff_member: Name des Mitarbeiters
            date: Datum der Abwesenheit
            reason: Grund (krank, Urlaub, etc.)
            context: Zusätzlicher Kontext
        
        Returns:
            Dict mit Status, Ersatz-Status, etc.
        """
        # Finde betroffene Schichten
        affected_shifts = [
            s for s in self.shifts
            if s.staff_member == staff_member and s.date == date
        ]
        
        if not affected_shifts:
            return {
                "status": "no_shifts_found",
                "message": f"Keine Schichten für {staff_member} am {date} gefunden."
            }
        
        # Markiere Schichten als Ersatz benötigt
        for shift in affected_shifts:
            shift.status = ShiftStatus.CANCELLED
            shift.replacement_needed = True
        
        # Versuche Ersatz zu finden
        replacement_result = self._find_replacement(affected_shifts)
        
        # Team informieren
        self._notify_team(affected_shifts, replacement_result)
        
        return {
            "status": "processed",
            "affected_shifts": len(affected_shifts),
            "replacement_found": replacement_result["found"],
            "message": replacement_result["message"]
        }
    
    def _find_replacement(
        self,
        shifts: List[Shift]
    ) -> Dict[str, Any]:
        """
        Findet Ersatz für Schichten
        
        Returns:
            Dict mit found, replacement_info
        """
        # TODO: Logik zum Finden von Ersatz
        # - Verfügbare Mitarbeiter prüfen
        # - Automatische Zuweisung wenn möglich
        # - Sonst Team-Benachrichtigung
        
        return {
            "found": False,
            "message": "Ersatz wird gesucht. Team wurde informiert."
        }
    
    def _notify_team(
        self,
        shifts: List[Shift],
        replacement_result: Dict[str, Any]
    ):
        """Informiert Team über Ausfälle"""
        # TODO: Via Communications Supervisor Team benachrichtigen
        pass
    
    def update_shift(
        self,
        shift_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aktualisiert Schicht
        
        Returns:
            Dict mit Status
        """
        shift = next((s for s in self.shifts if s.shift_id == shift_id), None)
        
        if not shift:
            return {"status": "error", "message": "Schicht nicht gefunden"}
        
        # Updates anwenden
        for key, value in updates.items():
            if hasattr(shift, key):
                setattr(shift, key, value)
        
        return {
            "status": "updated",
            "shift_id": shift_id
        }
    
    def get_shift_schedule(
        self,
        start_date: date,
        end_date: date
    ) -> List[Shift]:
        """Holt Schichtplan für Zeitraum"""
        return [
            s for s in self.shifts
            if start_date <= s.date <= end_date
        ]
