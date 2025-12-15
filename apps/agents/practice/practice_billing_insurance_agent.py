"""
Practice Billing Insurance Agent - Rechnungsfragen

Kann:
- Rechnungsfragen beantworten
- Privat/GKV-Standardtexte
- Zahlungslinks
- Mahnprozesse (ohne sensible Details preiszugeben)

V2 Add-on für Praxis-Paket
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class InsuranceType(str, Enum):
    """Versicherungstypen"""
    GKV = "gkv"  # Gesetzliche Krankenversicherung
    PKV = "pkv"  # Private Krankenversicherung
    SELF_PAY = "self_pay"  # Selbstzahler


class BillingStatus(str, Enum):
    """Rechnungs-Status"""
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


@dataclass
class BillingInquiry:
    """Rechnungsanfrage"""
    inquiry_id: str
    patient_id: str
    invoice_id: Optional[str] = None
    question: str = ""
    insurance_type: InsuranceType = InsuranceType.GKV
    status: str = "pending"
    created_at: datetime = None


class PracticeBillingInsuranceAgent:
    """
    Billing Insurance Agent für Rechnungsfragen
    
    Wichtig: Keine sensiblen Details preisgeben!
    
    V2 Add-on für Praxis-Paket
    """
    
    def __init__(self, account_id: str, integration_agent=None, communications_supervisor=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.communications_supervisor = communications_supervisor
        self.inquiries: List[BillingInquiry] = []
    
    def handle_billing_question(
        self,
        user_message: str,
        patient_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Rechnungsfrage
        
        Returns:
            Dict mit Antwort, Status
        """
        inquiry_id = f"BILL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Frage-Typ erkennen
        question_type = self._detect_question_type(user_message)
        
        # Standard-Antwort generieren
        answer = self._generate_standard_answer(question_type, context)
        
        inquiry = BillingInquiry(
            inquiry_id=inquiry_id,
            patient_id=patient_id or "unknown",
            question=user_message,
            status="answered",
            created_at=datetime.now()
        )
        
        self.inquiries.append(inquiry)
        
        return {
            "status": "answered",
            "answer": answer,
            "inquiry_id": inquiry_id
        }
    
    def _detect_question_type(self, message: str) -> str:
        """Erkennt Frage-Typ"""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ["rechnung", "rechnungsbetrag", "kosten"]):
            return "invoice_amount"
        
        if any(kw in message_lower for kw in ["zahlung", "bezahlen", "überweisen"]):
            return "payment"
        
        if any(kw in message_lower for kw in ["versicherung", "kasse", "gkv", "pkv"]):
            return "insurance"
        
        if any(kw in message_lower for kw in ["mahnung", "überfällig", "fällig"]):
            return "overdue"
        
        return "general"
    
    def _generate_standard_answer(
        self,
        question_type: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generiert Standard-Antwort"""
        answers = {
            "invoice_amount": """Gerne können wir Ihnen Auskunft über Ihre Rechnung geben. 
Bitte kontaktieren Sie uns telefonisch oder per E-Mail mit Ihrer Rechnungsnummer, 
damit wir Ihnen die Details mitteilen können.""",
            
            "payment": """Die Zahlung kann auf verschiedene Weise erfolgen:
- Überweisung auf unser Bankkonto (Details auf der Rechnung)
- Online-Zahlung per Link (falls verfügbar)
- Barzahlung bei Ihrem nächsten Besuch

Bitte kontaktieren Sie uns bei Fragen zur Zahlung.""",
            
            "insurance": """Wir arbeiten mit gesetzlichen und privaten Krankenversicherungen zusammen.
Bitte teilen Sie uns Ihre Versicherungsart mit, damit wir Ihnen genauere Informationen geben können.
Bei privaten Versicherungen können die Kosten variieren.""",
            
            "overdue": """Falls Ihre Rechnung überfällig ist, bitten wir um Kontaktaufnahme.
Wir finden gemeinsam eine Lösung. Bitte rufen Sie uns an oder senden Sie eine E-Mail.""",
            
            "general": """Gerne helfen wir Ihnen bei Fragen zu Rechnungen und Zahlungen weiter.
Bitte kontaktieren Sie uns telefonisch oder per E-Mail mit Ihrer Rechnungsnummer."""
        }
        
        return answers.get(question_type, answers["general"])
    
    def generate_payment_link(
        self,
        invoice_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Generiert Zahlungslink
        
        Returns:
            Dict mit payment_link, expires_at
        """
        # TODO: Via Integration Agent Payment-Link generieren
        
        return {
            "payment_link": f"https://pay.example.com/{invoice_id}",
            "expires_at": (datetime.now() + timedelta(days=14)).isoformat(),
            "amount": amount
        }
    
    def handle_overdue_invoice(
        self,
        invoice_id: str
    ) -> Dict[str, Any]:
        """
        Handhabt überfällige Rechnung
        
        Returns:
            Dict mit Status, Action
        """
        # TODO: Mahnprozess starten (ohne sensible Details)
        
        return {
            "status": "processed",
            "message": "Mahnung wurde versendet."
        }
