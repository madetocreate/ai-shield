"""
Gastronomy Supervisor Agent - Vertical Router für Gastro-Kontext

Erkennt Gastro-Kontext und routet sauber:
- Reservierung vs. Takeout vs. Allergene vs. Eventanfrage vs. Beschwerde
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum


class GastronomyIntent(str, Enum):
    """Gastro-spezifische Intents"""
    RESERVATION = "reservation"
    TAKEOUT_ORDER = "takeout_order"
    ALLERGEN_QUERY = "allergen_query"
    EVENT_CATERING = "event_catering"
    COMPLAINT = "complaint"
    GENERAL_INFO = "general_info"  # Öffnungszeiten, Adresse, etc.
    MENU_QUERY = "menu_query"
    REVIEW_RESPONSE = "review_response"


@dataclass
class RoutingDecision:
    """Routing-Entscheidung"""
    intent: GastronomyIntent
    target_agent: str
    confidence: float
    context: Dict[str, Any]


class GastronomySupervisorAgent:
    """
    Supervisor Agent für Gastronomie-Paket
    
    Routet Anfragen an spezialisierte Agents basierend auf Intent-Erkennung.
    """
    
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.intent_keywords = self._init_intent_keywords()
    
    def _init_intent_keywords(self) -> Dict[GastronomyIntent, List[str]]:
        """Initialisiert Keyword-Mapping für Intent-Erkennung"""
        return {
            GastronomyIntent.RESERVATION: [
                "reservierung", "tisch", "buchung", "tisch reservieren",
                "platz", "heute noch frei", "morgen", "wann habt ihr",
                "kann ich reservieren", "tisch für"
            ],
            GastronomyIntent.TAKEOUT_ORDER: [
                "bestellen", "takeout", "abholung", "zum mitnehmen",
                "lieferung", "bestellung", "ich möchte", "haben sie",
                "kann ich bestellen"
            ],
            GastronomyIntent.ALLERGEN_QUERY: [
                "allergen", "allergie", "glutenfrei", "vegan", "vegetarisch",
                "laktosefrei", "nüsse", "enthält", "allergene", "diät",
                "unverträglichkeit", "spuren"
            ],
            GastronomyIntent.EVENT_CATERING: [
                "event", "feier", "catering", "gruppen", "firma",
                "geburtstag", "hochzeit", "firmenfeier", "20 personen",
                "private dining", "geschlossene gesellschaft"
            ],
            GastronomyIntent.COMPLAINT: [
                "beschwerde", "unzufrieden", "schlecht", "probleme",
                "reklamation", "nicht zufrieden", "enttäuscht"
            ],
            GastronomyIntent.MENU_QUERY: [
                "menü", "karte", "was habt ihr", "angebot", "speisen",
                "getränke", "preis"
            ],
            GastronomyIntent.GENERAL_INFO: [
                "öffnungszeiten", "adresse", "parken", "wo seid ihr",
                "wie komme ich", "telefon", "kontakt"
            ],
        }
    
    def route_request(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Routet Anfrage basierend auf Intent-Erkennung
        
        Args:
            user_message: Benutzer-Nachricht
            context: Zusätzlicher Kontext (Channel, History, etc.)
        
        Returns:
            RoutingDecision mit Ziel-Agent
        """
        user_lower = user_message.lower()
        
        # Intent-Scoring
        intent_scores: Dict[GastronomyIntent, float] = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0.0
            matches = sum(1 for kw in keywords if kw in user_lower)
            if matches > 0:
                score = matches / len(keywords)
                # Boost für exakte Matches
                if any(kw == user_lower.strip() for kw in keywords):
                    score += 0.3
            
            if score > 0:
                intent_scores[intent] = score
        
        # Beste Intent finden
        if not intent_scores:
            # Fallback zu General Info
            intent = GastronomyIntent.GENERAL_INFO
            confidence = 0.5
        else:
            intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            confidence = intent_scores[intent]
        
        # Target Agent bestimmen
        target_agent = self._get_target_agent(intent)
        
        return RoutingDecision(
            intent=intent,
            target_agent=target_agent,
            confidence=confidence,
            context=context or {}
        )
    
    def _get_target_agent(self, intent: GastronomyIntent) -> str:
        """Mappt Intent zu Target Agent"""
        mapping = {
            GastronomyIntent.RESERVATION: "restaurant_voice_host_agent",
            GastronomyIntent.TAKEOUT_ORDER: "restaurant_takeout_order_agent",
            GastronomyIntent.ALLERGEN_QUERY: "restaurant_menu_allergen_agent",
            GastronomyIntent.EVENT_CATERING: "restaurant_events_catering_agent",
            GastronomyIntent.COMPLAINT: "support_resolution_agent",  # Bestehender Agent
            GastronomyIntent.MENU_QUERY: "restaurant_voice_host_agent",
            GastronomyIntent.GENERAL_INFO: "restaurant_voice_host_agent",
            GastronomyIntent.REVIEW_RESPONSE: "restaurant_reputation_agent",
        }
        return mapping.get(intent, "restaurant_voice_host_agent")
    
    def is_gastronomy_context(self, message: str) -> bool:
        """Prüft ob Nachricht Gastro-Kontext hat"""
        gastro_keywords = [
            "restaurant", "café", "cafe", "gastronomie", "essen",
            "speise", "getränk", "tisch", "reservierung", "bestellung",
            "menü", "karte", "küche", "gast", "bedienung"
        ]
        message_lower = message.lower()
        return any(kw in message_lower for kw in gastro_keywords)
