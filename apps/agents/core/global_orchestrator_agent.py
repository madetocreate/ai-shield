"""
Global Orchestrator Agent - Zentrale Routing-Logik (Legacy)

⚠️ DEPRECATED: Nutze LLMOrchestratorAgent für LLM-basierte Orchestration!

Dieser Orchestrator ist rein logik-basiert. Für intelligente Routing-Entscheidungen
nutze bitte LLMOrchestratorAgent (apps.agents.core.llm_orchestrator_agent).
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass

from apps.agents.shared.vertical_package_manifest import (
    get_registry as get_manifest_registry,
    PackageType
)
from apps.agents.core.agent_registry import get_registry as get_agent_registry
from apps.agents.shared.handoff_to_human_protocol import (
    get_protocol,
    HandoffReason
)
from apps.agents.shared.consent_and_redaction_gateway import (
    get_gateway as get_consent_gateway
)
from apps.agents.core.monitoring import get_monitor, RequestTracker
from apps.agents.core.intent_agent import get_intent_agent, IntentCategory


@dataclass
class RoutingRequest:
    """Routing-Anfrage"""
    account_id: str
    user_message: str
    channel: str  # phone, chat, email, sms, website
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class RoutingResponse:
    """Routing-Antwort"""
    target_agent: str
    agent_instance: Any
    requires_handoff: bool = False
    handoff_context: Optional[Any] = None
    requires_consent: bool = False
    redacted_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class GlobalOrchestratorAgent:
    """
    Global Orchestrator Agent
    
    Zentrale Routing-Logik die:
    1. Package Manifest lädt
    2. Basierend auf Package Type zum Vertical Supervisor routet
    3. Vertical Supervisor entscheidet über finalen Agent
    4. Consent/Redaction prüft
    5. Handoff-Protokoll anwendet
    """
    
    def __init__(self, llm_client=None):
        self.manifest_registry = get_manifest_registry()
        self.agent_registry = get_agent_registry()
        self.handoff_protocol = get_protocol()
        self.consent_gateway = get_consent_gateway()
        self.monitor = get_monitor()
        self.intent_agent = get_intent_agent(llm_client=llm_client)  # Intent Agent für schnelle Erkennung
    
    def route(
        self,
        request: RoutingRequest
    ) -> RoutingResponse:
        """
        Routet Request zu passendem Agent
        
        Args:
            request: Routing-Anfrage
        
        Returns:
            RoutingResponse mit Target Agent
        """
        # Monitoring: Request starten
        with RequestTracker("global_orchestrator", request.account_id):
            # 0. Intent erkennen (SCHNELL mit Intent Agent)
            intent_result = self.intent_agent.detect_intent(
                user_message=request.user_message,
                account_id=request.account_id,
                context=request.context
            )
            
            # 1. Package Manifest laden
            manifest = self.manifest_registry.get_manifest(request.account_id)
            
            # Wenn Intent Package Type erkannt hat, Manifest prüfen/erstellen
            if not manifest and intent_result.package_type:
                # Könnte hier automatisch Manifest erstellen oder Fallback nutzen
                pass
            
            if not manifest:
                # Fallback: Standard-Routing (kein Paket aktiviert)
                return self._fallback_routing(request, intent_result)
            
            # 2. Consent & Redaction prüfen
            consent_result = self._check_consent_and_redact(request, manifest)
        if not consent_result["allowed"]:
            # Handoff bei Consent-Problem
            handoff = self.handoff_protocol.should_handoff(
                account_id=request.account_id,
                user_id=request.user_id,
                channel=request.channel,
                conversation_id=request.conversation_id or "unknown",
                reason=HandoffReason.CONSENT_REQUIRED,
                context={"message": consent_result["message"]}
            )
            return RoutingResponse(
                target_agent="handoff",
                agent_instance=None,
                requires_handoff=True,
                handoff_context=handoff,
                requires_consent=True,
                metadata={"consent_error": consent_result["message"]}
            )
        
            # 3. Basierend auf Intent und Package Type routen (viel schneller mit Intent!)
            if intent_result.package_type == "gastronomy" or manifest.package_type == PackageType.GASTRONOMY:
                response = self._route_gastronomy(request, manifest, consent_result, intent_result)
            elif intent_result.package_type == "practice" or manifest.package_type == PackageType.PRACTICE:
                response = self._route_practice(request, manifest, consent_result, intent_result)
            else:
                response = self._fallback_routing(request, intent_result)
            
            # Monitoring: Routing-Entscheidung tracken
            if response.metadata and "intent" in response.metadata:
                self.monitor.track_routing_decision(
                    account_id=request.account_id,
                    source_agent="global_orchestrator",
                    target_agent=response.target_agent,
                    intent=response.metadata.get("intent", "unknown"),
                    confidence=response.metadata.get("confidence", 0.0)
                )
            
            # Monitoring: Handoff tracken
            if response.requires_handoff and response.handoff_context:
                self.monitor.track_handoff(
                    account_id=request.account_id,
                    reason=response.handoff_context.reason.value,
                    priority=response.handoff_context.priority.value,
                    method=response.handoff_context.method.value
                )
            
            return response
    
    def _route_gastronomy(
        self,
        request: RoutingRequest,
        manifest: Any,
        consent_result: Dict[str, Any],
        intent_result: Any
    ) -> RoutingResponse:
        """Routet Gastronomie-Request (mit vorerkanntem Intent - viel schneller!)"""
        
        # Direktes Routing basierend auf Intent (überspringt Supervisor wenn Intent klar ist)
        if intent_result.confidence > 0.8:
            target_agent = self._intent_to_agent_gastronomy(intent_result.intent)
            
            if target_agent and manifest.is_agent_enabled(target_agent):
                agent_instance = self.agent_registry.get_agent(
                    target_agent,
                    request.account_id
                )
                
                if agent_instance:
                    return RoutingResponse(
                        target_agent=target_agent,
                        agent_instance=agent_instance,
                        redacted_message=consent_result.get("redacted_message"),
                        metadata={
                            "intent": intent_result.intent.value,
                            "confidence": intent_result.confidence,
                            "package_type": "gastronomy",
                            "direct_routing": True,  # Schneller Pfad!
                            "entities": intent_result.entities
                        }
                    )
        
        # Fallback: Supervisor nutzen (wenn Intent unsicher)
        supervisor = self.agent_registry.get_agent(
            "gastronomy_supervisor_agent",
            request.account_id
        )
        
        if not supervisor:
            return self._fallback_routing(request, intent_result)
        
        # Supervisor routet basierend auf Intent (kann Intent nutzen)
        decision = supervisor.route_request(
            user_message=consent_result.get("redacted_message", request.user_message),
            context={
                "channel": request.channel,
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "detected_intent": intent_result.intent.value,  # Intent weitergeben
                "intent_confidence": intent_result.confidence,
                **(request.context or {})
            }
        )
        
        # Prüfe ob Agent aktiviert ist
        if not manifest.is_agent_enabled(decision.target_agent):
            # Fallback zu Voice Host
            decision.target_agent = "restaurant_voice_host_agent"
        
        # Agent-Instanz holen
        agent_instance = self.agent_registry.get_agent(
            decision.target_agent,
            request.account_id
        )
        
        if not agent_instance:
            return self._fallback_routing(request)
        
        return RoutingResponse(
            target_agent=decision.target_agent,
            agent_instance=agent_instance,
            redacted_message=consent_result.get("redacted_message"),
            metadata={
                "intent": decision.intent.value,
                "confidence": decision.confidence,
                "package_type": "gastronomy"
            }
        )
    
    def _route_practice(
        self,
        request: RoutingRequest,
        manifest: Any,
        consent_result: Dict[str, Any],
        intent_result: Any
    ) -> RoutingResponse:
        """Routet Praxis-Request mit Safety-Check (mit vorerkanntem Intent)"""
        
        # Safety-Check basierend auf Intent (viel schneller!)
        requires_safety = intent_result.requires_safety_check or intent_result.intent == IntentCategory.SYMPTOM_QUERY
        
        if requires_safety:
            privacy_guard = self.agent_registry.get_agent(
                "healthcare_privacy_guard_agent",
                request.account_id
            )
            
            if privacy_guard:
                validation = privacy_guard.validate_request(
                    use_case="general",
                    collected_data={},
                    content=consent_result.get("redacted_message", request.user_message)
                )
                
                if not validation.allowed:
                    handoff = self.handoff_protocol.should_handoff(
                        account_id=request.account_id,
                        user_id=request.user_id,
                        channel=request.channel,
                        conversation_id=request.conversation_id or "unknown",
                        reason=HandoffReason.SAFETY_CONCERN,
                        context={
                            "violation": validation.violation_type.value if validation.violation_type else "unknown",
                            "message": validation.message
                        }
                    )
                    return RoutingResponse(
                        target_agent="handoff",
                        agent_instance=None,
                        requires_handoff=True,
                        handoff_context=handoff,
                        metadata={
                            "safety_check_failed": True,
                            "intent": intent_result.intent.value
                        }
                    )
        
        # Direktes Routing basierend auf Intent (wenn sicher)
        if intent_result.confidence > 0.8 and not requires_safety:
            target_agent = self._intent_to_agent_practice(intent_result.intent)
            
            if target_agent and manifest.is_agent_enabled(target_agent):
                agent_instance = self.agent_registry.get_agent(
                    target_agent,
                    request.account_id
                )
                
                if agent_instance:
                    return RoutingResponse(
                        target_agent=target_agent,
                        agent_instance=agent_instance,
                        redacted_message=consent_result.get("redacted_message"),
                        metadata={
                            "intent": intent_result.intent.value,
                            "confidence": intent_result.confidence,
                            "package_type": "practice",
                            "direct_routing": True,
                            "entities": intent_result.entities
                        }
                    )
        
        # Fallback: Supervisor nutzen
        supervisor = self.agent_registry.get_agent(
            "practice_supervisor_agent",
            request.account_id
        )
        
        if not supervisor:
            return self._fallback_routing(request, intent_result)
        
        # Supervisor routet (kann Intent nutzen)
        decision = supervisor.route_request(
            user_message=consent_result.get("redacted_message", request.user_message),
            context={
                "channel": request.channel,
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "detected_intent": intent_result.intent.value,
                "intent_confidence": intent_result.confidence,
                **(request.context or {})
            }
        )
        
        # Safety-Check wenn erforderlich (aus Supervisor)
        if decision.requires_safety_check:
            privacy_guard = self.agent_registry.get_agent(
                "healthcare_privacy_guard_agent",
                request.account_id
            )
            
            if privacy_guard:
                validation = privacy_guard.validate_request(
                    use_case="general",
                    collected_data={},
                    content=consent_result.get("redacted_message", request.user_message)
                )
                
                if not validation.allowed:
                    # Handoff bei Privacy-Verletzung
                    handoff = self.handoff_protocol.should_handoff(
                        account_id=request.account_id,
                        user_id=request.user_id,
                        channel=request.channel,
                        conversation_id=request.conversation_id or "unknown",
                        reason=HandoffReason.SAFETY_CONCERN,
                        context={
                            "violation": validation.violation_type.value if validation.violation_type else "unknown",
                            "message": validation.message
                        }
                    )
                    return RoutingResponse(
                        target_agent="handoff",
                        agent_instance=None,
                        requires_handoff=True,
                        handoff_context=handoff,
                        metadata={
                            "safety_check_failed": True,
                            "violation": validation.violation_type.value if validation.violation_type else None
                        }
                    )
        
        # Prüfe ob Agent aktiviert ist
        if not manifest.is_agent_enabled(decision.target_agent):
            # Fallback zu Phone Reception
            decision.target_agent = "practice_phone_reception_agent"
        
        # Agent-Instanz holen
        agent_instance = self.agent_registry.get_agent(
            decision.target_agent,
            request.account_id
        )
        
        if not agent_instance:
            return self._fallback_routing(request)
        
        return RoutingResponse(
            target_agent=decision.target_agent,
            agent_instance=agent_instance,
            redacted_message=consent_result.get("redacted_message"),
            metadata={
                "intent": decision.intent.value,
                "confidence": decision.confidence,
                "package_type": "practice",
                "requires_safety_check": decision.requires_safety_check
            }
        )
    
    def _check_consent_and_redact(
        self,
        request: RoutingRequest,
        manifest: Any
    ) -> Dict[str, Any]:
        """Prüft Consent und redactiert Content"""
        # Redaction durchführen
        redacted, categories = self.consent_gateway.redact_content(
            content=request.user_message,
            account_id=request.account_id,
            user_id=request.user_id,
            require_consent=manifest.policies.require_consent
        )
        
        # Consent prüfen (wenn erforderlich)
        if manifest.policies.require_consent:
            # TODO: Spezifische Consent-Checks basierend auf Package Type
            # Für jetzt: Basic Check
            has_consent = True  # TODO: Implementieren
        
        return {
            "allowed": True,  # TODO: Basierend auf Consent-Check
            "redacted_message": redacted,
            "redacted_categories": categories
        }
    
    def _intent_to_agent_gastronomy(self, intent: IntentCategory) -> Optional[str]:
        """Mappt Intent zu Gastronomie-Agent"""
        mapping = {
            IntentCategory.RESERVATION: "restaurant_voice_host_agent",
            IntentCategory.TAKEOUT_ORDER: "restaurant_takeout_order_agent",
            IntentCategory.ALLERGEN_QUERY: "restaurant_menu_allergen_agent",
            IntentCategory.EVENT_CATERING: "restaurant_events_catering_agent",
            IntentCategory.MENU_QUERY: "restaurant_voice_host_agent",
            IntentCategory.GENERAL_INFO: "restaurant_voice_host_agent",
            IntentCategory.COMPLAINT: "support_resolution_agent",
            IntentCategory.REVIEW: "restaurant_reputation_agent",
        }
        return mapping.get(intent)
    
    def _intent_to_agent_practice(self, intent: IntentCategory) -> Optional[str]:
        """Mappt Intent zu Praxis-Agent"""
        mapping = {
            IntentCategory.APPOINTMENT: "practice_phone_reception_agent",
            IntentCategory.PRESCRIPTION: "practice_admin_requests_agent",
            IntentCategory.REFERRAL: "practice_admin_requests_agent",
            IntentCategory.FORM_REQUEST: "practice_patient_intake_forms_agent",
            IntentCategory.BILLING: "practice_admin_requests_agent",
            IntentCategory.SYMPTOM_QUERY: "practice_phone_reception_agent",
            IntentCategory.ADMIN_REQUEST: "practice_admin_requests_agent",
            IntentCategory.GENERAL_INFO: "practice_phone_reception_agent",
        }
        return mapping.get(intent)
    
    def _fallback_routing(
        self,
        request: RoutingRequest,
        intent_result: Any = None
    ) -> RoutingResponse:
        """Fallback-Routing wenn kein Paket aktiviert"""
        # Versuche basierend auf Intent zu routen
        if intent_result and intent_result.package_type:
            if intent_result.package_type == "gastronomy":
                target = self._intent_to_agent_gastronomy(intent_result.intent)
            elif intent_result.package_type == "practice":
                target = self._intent_to_agent_practice(intent_result.intent)
            else:
                target = None
            
            if target:
                agent_instance = self.agent_registry.get_agent(target, request.account_id)
                if agent_instance:
                    return RoutingResponse(
                        target_agent=target,
                        agent_instance=agent_instance,
                        metadata={
                            "fallback": True,
                            "intent": intent_result.intent.value,
                            "reason": "no_package_manifest"
                        }
                    )
        
        return RoutingResponse(
            target_agent="support_triage_agent",  # Fallback
            agent_instance=None,
            metadata={"fallback": True, "reason": "no_package_manifest"}
        )


# Globale Orchestrator-Instanz
_global_orchestrator: Optional[GlobalOrchestratorAgent] = None


def get_orchestrator() -> GlobalOrchestratorAgent:
    """Holt globale Orchestrator-Instanz"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = GlobalOrchestratorAgent()
    return _global_orchestrator
