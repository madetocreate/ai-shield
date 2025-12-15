"""
Practice Supervisor Agent - Vertical Router für Praxis-Kontext

Erkennt:
- Termin, Rezeptwunsch, Überweisung, Formular, Rechnung
- "Ich hab Symptome" (→ sicherer Pfad)
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum


class PracticeIntent(str, Enum):
    """Praxis-spezifische Intents"""
    APPOINTMENT = "appointment"
    PRESCRIPTION_REQUEST = "prescription_request"
    REFERRAL_REQUEST = "referral_request"
    FORM_REQUEST = "form_request"
    BILLING_QUESTION = "billing_question"
    SYMPTOM_QUERY = "symptom_query"  # → Safety Routing!
    ADMIN_REQUEST = "admin_request"
    GENERAL_INFO = "general_info"  # Öffnungszeiten, etc.


@dataclass
class RoutingDecision:
    """Routing-Entscheidung"""
    intent: PracticeIntent
    target_agent: str
    confidence: float
    requires_safety_check: bool = False
    context: Dict[str, Any] = None


class PracticeSupervisorAgent:
    """
    Supervisor Agent für Praxis-Paket
    
    Routet Anfragen an spezialisierte Agents, mit besonderer Aufmerksamkeit
    für medizinische Inhalte (Safety Routing).
    """
    
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.intent_keywords = self._init_intent_keywords()
        self.safety_keywords = self._init_safety_keywords()
    
    def _init_intent_keywords(self) -> Dict[PracticeIntent, List[str]]:
        """Initialisiert Keyword-Mapping für Intent-Erkennung"""
        return {
            PracticeIntent.APPOINTMENT: [
                "termin", "termin vereinbaren", "wann", "verfügbar",
                "verschieben", "stornieren", "absagen", "neuer termin"
            ],
            PracticeIntent.PRESCRIPTION_REQUEST: [
                "rezept", "medikament", "arzneimittel", "rezeptanfrage",
                "brauche rezept", "rezept bestellen"
            ],
            PracticeIntent.REFERRAL_REQUEST: [
                "überweisung", "überweisungsschein", "weisung",
                "zu spezialist", "facharzt"
            ],
            PracticeIntent.FORM_REQUEST: [
                "formular", "anmeldung", "anamnese", "einverständnis",
                "versicherung", "datenschutz"
            ],
            PracticeIntent.BILLING_QUESTION: [
                "rechnung", "kosten", "zahlung", "versicherung",
                "privat", "kasse", "abrechnung"
            ],
            PracticeIntent.SYMPTOM_QUERY: [
                "symptom", "schmerzen", "weh", "krank", "fieber",
                "übelkeit", "beschwerden", "probleme", "habe ich"
            ],
            PracticeIntent.ADMIN_REQUEST: [
                "befund", "befundkopie", "attest", "au", "krankschreibung",
                "bescheinigung", "dokument"
            ],
            PracticeIntent.GENERAL_INFO: [
                "öffnungszeiten", "adresse", "wo", "erreichen",
                "telefon", "kontakt"
            ],
        }
    
    def _init_safety_keywords(self) -> List[str]:
        """Keywords die Safety-Check auslösen"""
        return [
            "symptom", "schmerzen", "krank", "fieber", "notfall",
            "akut", "schlecht", "schlimm", "besorgt", "sorge",
            "herz", "atem", "atemnot", "brustschmerz", "schwindel"
        ]
    
    def route_request(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Routet Anfrage basierend auf Intent-Erkennung
        
        Wichtig: Erkennt medizinische Inhalte und aktiviert Safety-Check.
        
        Args:
            user_message: Benutzer-Nachricht
            context: Zusätzlicher Kontext
        
        Returns:
            RoutingDecision mit Ziel-Agent und Safety-Flag
        """
        user_lower = user_message.lower()
        
        # Safety-Check zuerst
        requires_safety_check = any(
            kw in user_lower for kw in self.safety_keywords
        )
        
        # Intent-Scoring
        intent_scores: Dict[PracticeIntent, float] = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0.0
            matches = sum(1 for kw in keywords if kw in user_lower)
            if matches > 0:
                score = matches / len(keywords)
                if any(kw == user_lower.strip() for kw in keywords):
                    score += 0.3
            
            if score > 0:
                intent_scores[intent] = score
        
        # Beste Intent finden
        if not intent_scores:
            intent = PracticeIntent.GENERAL_INFO
            confidence = 0.5
        else:
            intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            confidence = intent_scores[intent]
        
        # Safety-Check für Symptom-Queries
        if intent == PracticeIntent.SYMPTOM_QUERY:
            requires_safety_check = True
        
        # Target Agent bestimmen
        target_agent = self._get_target_agent(intent)
        
        return RoutingDecision(
            intent=intent,
            target_agent=target_agent,
            confidence=confidence,
            requires_safety_check=requires_safety_check,
            context=context or {}
        )
    
    def _get_target_agent(self, intent: PracticeIntent) -> str:
        """Mappt Intent zu Target Agent"""
        mapping = {
            PracticeIntent.APPOINTMENT: "practice_phone_reception_agent",
            PracticeIntent.PRESCRIPTION_REQUEST: "practice_admin_requests_agent",
            PracticeIntent.REFERRAL_REQUEST: "practice_admin_requests_agent",
            PracticeIntent.FORM_REQUEST: "practice_patient_intake_forms_agent",
            PracticeIntent.BILLING_QUESTION: "practice_admin_requests_agent",
            PracticeIntent.SYMPTOM_QUERY: "practice_phone_reception_agent",  # → Safety Routing
            PracticeIntent.ADMIN_REQUEST: "practice_admin_requests_agent",
            PracticeIntent.GENERAL_INFO: "practice_phone_reception_agent",
        }
        return mapping.get(intent, "practice_phone_reception_agent")
    
    def is_practice_context(self, message: str) -> bool:
        """Prüft ob Nachricht Praxis-Kontext hat"""
        practice_keywords = [
            "praxis", "arzt", "doktor", "termin", "patient",
            "rezept", "überweisung", "befund", "krank", "symptom"
        ]
        message_lower = message.lower()
        return any(kw in message_lower for kw in practice_keywords)
