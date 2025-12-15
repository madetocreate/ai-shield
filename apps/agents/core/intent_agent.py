"""
Intent Agent - Schnelle Intent-Erkennung mit LLM

Nutzt gpt-4o-mini für schnelle, präzise Intent-Erkennung.
Erkennt Intent BEVOR der Orchestrator routet → viel schneller!
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import json
import os

# Globale Intent Agent-Instanz
_global_intent_agent: Optional['IntentAgent'] = None


class IntentCategory(str, Enum):
    """Intent-Kategorien (unabhängig von Package Type)"""
    # Gastronomie
    RESERVATION = "reservation"
    TAKEOUT_ORDER = "takeout_order"
    ALLERGEN_QUERY = "allergen_query"
    EVENT_CATERING = "event_catering"
    MENU_QUERY = "menu_query"
    GENERAL_INFO = "general_info"
    COMPLAINT = "complaint"
    REVIEW = "review"
    
    # Praxis
    APPOINTMENT = "appointment"
    PRESCRIPTION = "prescription"
    REFERRAL = "referral"
    FORM_REQUEST = "form_request"
    BILLING = "billing"
    SYMPTOM_QUERY = "symptom_query"
    ADMIN_REQUEST = "admin_request"
    
    # Allgemein
    UNKNOWN = "unknown"
    HANDOFF_REQUIRED = "handoff_required"


@dataclass
class IntentResult:
    """Intent-Erkennungs-Ergebnis"""
    intent: IntentCategory
    confidence: float
    package_type: Optional[str] = None  # "gastronomy" oder "practice"
    requires_safety_check: bool = False
    entities: Dict[str, Any] = None  # Extrahierte Entities (Datum, Zeit, etc.)
    reasoning: Optional[str] = None
    recommended_agents: List[str] = None  # Gefilterte Agents für Orchestrator


class IntentAgent:
    """
    Intent Agent für schnelle Intent-Erkennung
    
    Nutzt LLM (gpt-4o-mini) für präzise Intent-Erkennung.
    Viel schneller als Keyword-Matching und genauer.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialisiert Intent Agent
        
        Args:
            llm_client: LLM Client (z.B. OpenAI, LiteLLM). Falls None, wird LiteLLM genutzt.
        """
        self.llm_client = llm_client
        self.model = os.getenv("INTENT_AGENT_MODEL", "gpt-4o-mini")  # Schnelles, günstiges Modell
        self._setup_llm()
    
    def _setup_llm(self):
        """Setzt LLM Client auf"""
        if self.llm_client is None:
            try:
                # Versuche LiteLLM zu nutzen (falls verfügbar)
                import litellm
                self.llm_client = litellm
            except ImportError:
                try:
                    # Fallback zu OpenAI
                    import openai
                    self.llm_client = openai
                except ImportError:
                    self.llm_client = None
                    print("WARNING: Kein LLM Client verfügbar. Intent-Erkennung wird auf Keyword-Matching zurückfallen.")
    
    def detect_intent(
        self,
        user_message: str,
        account_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentResult:
        """
        Erkennt Intent und filtert verfügbare Agents
        
        Returns:
            IntentResult mit gefilterten Agents für Orchestrator
        """
        """
        Erkennt Intent aus User-Nachricht
        
        Args:
            user_message: Benutzer-Nachricht
            account_id: Account-ID (für Package-Type-Hinweis)
            context: Zusätzlicher Kontext
        
        Returns:
            IntentResult mit erkanntem Intent
        """
        # Wenn kein LLM verfügbar, Fallback zu Keyword-Matching
        if not self.llm_client:
            return self._fallback_intent_detection(user_message, account_id)
        
        # LLM-basierte Intent-Erkennung
        try:
            return self._llm_intent_detection(user_message, account_id, context)
        except Exception as e:
            print(f"Fehler bei LLM Intent-Erkennung: {e}")
            return self._fallback_intent_detection(user_message, account_id)
    
    def _llm_intent_detection(
        self,
        user_message: str,
        account_id: str,
        context: Optional[Dict[str, Any]]
    ) -> IntentResult:
        """LLM-basierte Intent-Erkennung"""
        
        # Prompt für Intent-Erkennung
        prompt = self._build_intent_prompt(user_message, account_id, context)
        
        # LLM Call (schnell mit gpt-4o-mini)
        if hasattr(self.llm_client, 'completion'):
            # LiteLLM
            response = self.llm_client.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Niedrig für konsistente Ergebnisse
                max_tokens=200,  # Kurz für Geschwindigkeit
                response_format={"type": "json_object"}  # Strukturierte Antwort
            )
            result_json = json.loads(response.choices[0].message.content)
        elif hasattr(self.llm_client, 'chat'):
            # OpenAI direkt
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            result_json = json.loads(response.choices[0].message.content)
        else:
            # Fallback
            return self._fallback_intent_detection(user_message, account_id)
        
        # Parse Ergebnis
        intent_str = result_json.get("intent", "unknown")
        confidence = float(result_json.get("confidence", 0.5))
        package_type = result_json.get("package_type")
        requires_safety = result_json.get("requires_safety_check", False)
        entities = result_json.get("entities", {})
        reasoning = result_json.get("reasoning")
        
        # Filter Agents basierend auf Intent
        recommended_agents = self._filter_agents_for_intent(
            intent_str, package_type
        )
        
        return IntentResult(
            intent=IntentCategory(intent_str) if intent_str in [e.value for e in IntentCategory] else IntentCategory.UNKNOWN,
            confidence=confidence,
            package_type=package_type,
            requires_safety_check=requires_safety,
            entities=entities,
            reasoning=reasoning,
            recommended_agents=recommended_agents
        )
    
    def _get_system_prompt(self) -> str:
        """System Prompt für Intent-Erkennung (nutzt Best Practices)"""
        from apps.agents.core.prompt_templates import IntentAgentPromptBuilder
        from apps.agents.core.caching import cached
        
        # Cache Intent-Erkennung (5 Minuten)
        @cached(ttl=300)
        def _cached_detect(self, message_hash: str):
            return IntentAgentPromptBuilder.build_system_prompt()
        
        return IntentAgentPromptBuilder.build_system_prompt()
    
    def _build_intent_prompt(
        self,
        user_message: str,
        account_id: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Baut Prompt für Intent-Erkennung"""
        prompt = f"Erkenne den Intent dieser Nachricht:\n\n{user_message}\n\n"
        
        if context:
            prompt += f"\nKontext: {json.dumps(context, ensure_ascii=False)}\n"
        
        prompt += "\nAntworte im JSON-Format mit intent, confidence, package_type, requires_safety_check, entities, reasoning."
        
        return prompt
    
    def _filter_agents_for_intent(
        self,
        intent: str,
        package_type: Optional[str]
    ) -> List[str]:
        """
        Filtert verfügbare Agents basierend auf Intent
        
        Reduziert Tool-Auswahl für Orchestrator (Best Practice).
        """
        # Intent → Agent Mapping
        intent_to_agents = {
            # Gastronomie
            "reservation": ["restaurant_voice_host_agent", "gastronomy_supervisor_agent"],
            "takeout_order": ["restaurant_takeout_order_agent", "gastronomy_supervisor_agent"],
            "allergen_query": ["restaurant_menu_allergen_agent", "restaurant_voice_host_agent"],
            "event_catering": ["restaurant_events_catering_agent", "gastronomy_supervisor_agent"],
            "menu_query": ["restaurant_voice_host_agent", "gastronomy_supervisor_agent"],
            "general_info": ["restaurant_voice_host_agent", "gastronomy_supervisor_agent"],
            "complaint": ["support_resolution_agent", "restaurant_voice_host_agent"],
            "review": ["restaurant_reputation_agent", "gastronomy_supervisor_agent"],
            
            # Praxis
            "appointment": ["practice_phone_reception_agent", "practice_supervisor_agent"],
            "prescription": ["practice_admin_requests_agent", "practice_supervisor_agent"],
            "referral": ["practice_admin_requests_agent", "practice_supervisor_agent"],
            "form_request": ["practice_patient_intake_forms_agent", "practice_supervisor_agent"],
            "billing": ["practice_admin_requests_agent", "practice_supervisor_agent"],
            "symptom_query": ["practice_phone_reception_agent", "healthcare_privacy_guard_agent", "practice_supervisor_agent"],
            "admin_request": ["practice_admin_requests_agent", "practice_supervisor_agent"],
        }
        
        # Hole empfohlene Agents für Intent
        agents = intent_to_agents.get(intent, [])
        
        # Filter basierend auf Package Type
        if package_type:
            filtered = []
            for agent in agents:
                # Prüfe ob Agent zum Package passt
                if package_type == "gastronomy" and ("restaurant" in agent or "gastronomy" in agent or "support" in agent):
                    filtered.append(agent)
                elif package_type == "practice" and ("practice" in agent or "healthcare" in agent or "support" in agent):
                    filtered.append(agent)
                elif package_type == "general":
                    filtered.append(agent)
            
            return filtered if filtered else agents
        
        return agents
    
    def _fallback_intent_detection(
        self,
        user_message: str,
        account_id: str
    ) -> IntentResult:
        """Fallback: Keyword-basierte Intent-Erkennung"""
        user_lower = user_message.lower()
        
        # Gastronomie-Keywords
        if any(kw in user_lower for kw in ["reservierung", "tisch", "buchung"]):
            return IntentResult(
                intent=IntentCategory.RESERVATION,
                confidence=0.7,
                package_type="gastronomy"
            )
        
        if any(kw in user_lower for kw in ["bestellen", "takeout", "abholung"]):
            return IntentResult(
                intent=IntentCategory.TAKEOUT_ORDER,
                confidence=0.7,
                package_type="gastronomy"
            )
        
        # Praxis-Keywords
        if any(kw in user_lower for kw in ["termin", "vereinbaren", "wann"]):
            return IntentResult(
                intent=IntentCategory.APPOINTMENT,
                confidence=0.7,
                package_type="practice"
            )
        
        if any(kw in user_lower for kw in ["symptom", "schmerzen", "krank"]):
            return IntentResult(
                intent=IntentCategory.SYMPTOM_QUERY,
                confidence=0.7,
                package_type="practice",
                requires_safety_check=True
            )
        
        # Default
        return IntentResult(
            intent=IntentCategory.UNKNOWN,
            confidence=0.3,
            recommended_agents=["support_triage_agent"]
        )


def get_intent_agent(llm_client=None) -> 'IntentAgent':
    """Holt globale Intent Agent-Instanz"""
    global _global_intent_agent
    if _global_intent_agent is None:
        _global_intent_agent = IntentAgent(llm_client=llm_client)
    return _global_intent_agent
