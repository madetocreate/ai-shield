"""
Restaurant Menu Allergen Agent - Menü + Allergene + Diäten

Kann:
- "Ist glutenfrei?", "enthält Nüsse?", "vegan?" beantworten
- Konsistent aus eigener Datenquelle (Menü + Rezeptbuch/Allergenmatrix)
- Wording-Guardrails (Spuren/Kreuzkontamination/"bitte Personal informieren")

Wichtig: Allergeninformation ist in der Gastro für unverpackte Ware verpflichtend.
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum


class AllergenType(str, Enum):
    """Allergen-Typen nach EU-Verordnung"""
    GLUTEN = "gluten"
    MILK = "milk"
    EGGS = "eggs"
    FISH = "fish"
    SHELLFISH = "shellfish"
    TREE_NUTS = "tree_nuts"
    PEANUTS = "peanuts"
    SOY = "soy"
    SESAME = "sesame"
    SULPHITES = "sulphites"
    LUPIN = "lupin"
    MOLLUSCS = "molluscs"
    MUSTARD = "mustard"
    CELERY = "celery"


class DietType(str, Enum):
    """Diät-Typen"""
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    LACTOSE_FREE = "lactose_free"
    HALAL = "halal"
    KOSHER = "kosher"


@dataclass
class AllergenInfo:
    """Allergen-Information für ein Gericht"""
    dish_name: str
    allergens: List[AllergenType]
    diets: List[DietType]
    may_contain_traces: List[AllergenType]  # Spuren möglich
    cross_contamination_risk: bool = False
    requires_staff_notification: bool = False


class RestaurantMenuAllergenAgent:
    """
    Menu Allergen Agent für Allergen- und Diät-Auskünfte
    
    Wichtig: Strikte Guardrails für rechtssichere Auskünfte.
    """
    
    def __init__(self, account_id: str, knowledge_base_agent=None, document_intelligence_agent=None):
        self.account_id = account_id
        self.knowledge_base_agent = knowledge_base_agent
        self.document_intelligence_agent = document_intelligence_agent
        self.allergen_matrix: Dict[str, AllergenInfo] = {}
        self._load_allergen_data()
    
    def _load_allergen_data(self):
        """Lädt Allergen-Matrix aus Knowledge Base"""
        # TODO: Via Knowledge Base Agent laden
        # TODO: Via Document Intelligence Agent Menü-PDFs verarbeiten
        pass
    
    def check_allergen(
        self,
        dish_name: str,
        allergen: AllergenType
    ) -> Dict[str, Any]:
        """
        Prüft ob Gericht bestimmtes Allergen enthält
        
        Returns:
            Dict mit contains, may_contain_traces, requires_staff_notification
        """
        info = self.allergen_matrix.get(dish_name.lower())
        
        if not info:
            return {
                "contains": None,  # Unbekannt
                "may_contain_traces": True,  # Sicherheitshalber
                "requires_staff_notification": True,
                "message": f"Zu '{dish_name}' kann ich keine genauen Allergeninformationen geben. Bitte informieren Sie unser Personal bei der Bestellung."
            }
        
        contains = allergen in info.allergens
        may_contain = allergen in info.may_contain_traces or info.cross_contamination_risk
        
        return {
            "contains": contains,
            "may_contain_traces": may_contain,
            "requires_staff_notification": info.requires_staff_notification or may_contain,
            "message": self._format_allergen_response(dish_name, allergen, contains, may_contain)
        }
    
    def check_diet(
        self,
        dish_name: str,
        diet: DietType
    ) -> Dict[str, Any]:
        """
        Prüft ob Gericht für bestimmte Diät geeignet ist
        
        Returns:
            Dict mit suitable, message
        """
        info = self.allergen_matrix.get(dish_name.lower())
        
        if not info:
            return {
                "suitable": None,
                "message": f"Zu '{dish_name}' kann ich keine genauen Diätinformationen geben. Bitte informieren Sie unser Personal."
            }
        
        suitable = diet in info.diets
        
        return {
            "suitable": suitable,
            "message": self._format_diet_response(dish_name, diet, suitable)
        }
    
    def _format_allergen_response(
        self,
        dish_name: str,
        allergen: AllergenType,
        contains: bool,
        may_contain: bool
    ) -> str:
        """Formatiert Allergen-Antwort mit Guardrails"""
        allergen_names = {
            AllergenType.GLUTEN: "Gluten",
            AllergenType.MILK: "Milch",
            AllergenType.EGGS: "Eier",
            AllergenType.NUTS: "Nüsse",
            # ... weitere
        }
        allergen_name = allergen_names.get(allergen, allergen.value)
        
        if contains:
            return f"'{dish_name}' enthält {allergen_name}. Bitte informieren Sie unser Personal bei der Bestellung über Ihre Allergie."
        
        if may_contain:
            return f"'{dish_name}' enthält nach unserem Wissen kein {allergen_name}, jedoch können Spuren nicht ausgeschlossen werden. Bitte informieren Sie unser Personal bei der Bestellung."
        
        return f"'{dish_name}' enthält nach unserem Wissen kein {allergen_name}. Bitte informieren Sie unser Personal bei der Bestellung über Ihre Allergie."
    
    def _format_diet_response(
        self,
        dish_name: str,
        diet: DietType,
        suitable: bool
    ) -> str:
        """Formatiert Diät-Antwort"""
        diet_names = {
            DietType.VEGAN: "vegan",
            DietType.VEGETARIAN: "vegetarisch",
            DietType.GLUTEN_FREE: "glutenfrei",
            DietType.LACTOSE_FREE: "laktosefrei",
        }
        diet_name = diet_names.get(diet, diet.value)
        
        if suitable:
            return f"Ja, '{dish_name}' ist {diet_name}."
        else:
            return f"Nein, '{dish_name}' ist nicht {diet_name}. Bitte informieren Sie unser Personal für Alternativen."
    
    def handle_allergen_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Verarbeitet Allergen-Anfrage
        
        Returns:
            Antwort-Text mit Guardrails
        """
        query_lower = query.lower()
        
        # TODO: NLP um Gericht und Allergen/Diät zu extrahieren
        # TODO: Via check_allergen/check_diet prüfen
        # TODO: Antwort mit Guardrails formatieren
        
        return "Bitte informieren Sie unser Personal bei der Bestellung über Ihre Allergien oder Unverträglichkeiten."
