"""
LLM-Based Orchestrator Agent - Intelligenter Orchestrator mit LLM

Nutzt GPT-5.2 (oder neuestes verfügbares Modell) für intelligente Routing-Entscheidungen.
Basiert auf OpenAI Agent SDK Patterns und LLM-Driven Orchestration.
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
import os
import json
import logging

logger = logging.getLogger(__name__)

# Globale Orchestrator-Instanz
_global_llm_orchestrator: Optional['LLMOrchestratorAgent'] = None

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
from apps.agents.core.web_search_tool import get_web_search_tool
from apps.agents.core.mcp_tool_registry import get_mcp_tool_registry
from apps.agents.core.error_handling import get_error_handler, retry_with_backoff, graceful_degradation
from apps.agents.core.rate_limiting import get_rate_limiter, RateLimitConfig
from datetime import datetime
import asyncio


@dataclass
class RoutingRequest:
    """Routing-Anfrage"""
    account_id: str
    user_message: str
    channel: str  # phone, chat, email, sms, website
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


@dataclass
class RoutingResponse:
    """Routing-Antwort"""
    target_agent: str
    agent_instance: Any
    reasoning: str  # LLM-Begründung für Routing-Entscheidung
    confidence: float
    requires_handoff: bool = False
    handoff_context: Optional[Any] = None
    requires_consent: bool = False
    redacted_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class LLMOrchestratorAgent:
    """
    LLM-Based Orchestrator Agent
    
    Nutzt GPT-5.2 (oder neuestes Modell) für intelligente Routing-Entscheidungen.
    Basiert auf OpenAI Agent SDK Patterns:
    - LLM-Driven Orchestration
    - Tool-based Agent Selection
    - Intelligent Reasoning
    """
    
    def __init__(self, llm_client=None):
        """
        Initialisiert LLM Orchestrator
        
        Args:
            llm_client: LLM Client (LiteLLM oder OpenAI). Falls None, wird automatisch erkannt.
        """
        self.manifest_registry = get_manifest_registry()
        self.agent_registry = get_agent_registry()
        self.handoff_protocol = get_protocol()
        self.consent_gateway = get_consent_gateway()
        self.monitor = get_monitor()
        self.web_search_tool = get_web_search_tool()  # Web Search Tool
        self.mcp_tool_registry = get_mcp_tool_registry()  # MCP Tool Registry
        self.error_handler = get_error_handler()  # Error Handling
        self.rate_limiter = get_rate_limiter()  # Rate Limiting
        
        # Distributed Tracing
        from apps.agents.core.distributed_tracing import get_tracer
        self.tracer = get_tracer(service_name="llm_orchestrator")
        
        # Event Bus
        from apps.agents.core.webhooks import get_event_bus, EventType, Event
        self.event_bus = get_event_bus()
        
        # Cost Tracking
        from apps.agents.core.cost_tracking import get_cost_tracker, CostType
        self.cost_tracker = get_cost_tracker()
        
        # Real-time Monitoring
        from apps.agents.core.real_time_monitoring import get_real_time_monitor, RealTimeMetric
        self.real_time_monitor = get_real_time_monitor()
        
        # Multi-Language Support
        from apps.agents.core.multi_language import get_language_detector, get_translator, get_localization_manager, Language
        self.language_detector = get_language_detector()
        self.translator = get_translator()
        self.localization = get_localization_manager()
        self.default_language = Language(os.getenv("DEFAULT_LANGUAGE", "de"))
        
        # LLM Konfiguration
        self.llm_client = llm_client
        # Nutze neuestes Modell: GPT-5.2 (falls verfügbar), sonst GPT-5.1, sonst GPT-5, sonst GPT-4o
        self.model = os.getenv(
            "ORCHESTRATOR_MODEL",
            os.getenv("ORCHESTRATOR_MODEL", "gpt-5.2")  # Neuestes Modell
        )
        
        # Fallback-Kette für Modell-Verfügbarkeit
        self.model_fallback_chain = [
            "gpt-5.2",  # Neuestes (Dezember 2025)
            "gpt-5.1",  # November 2025
            "gpt-5",    # August 2025
            "gpt-4.1",  # April 2025
            "gpt-4o",   # May 2024
        ]
        
        self._setup_llm()
        self._setup_tools()
    
    def _setup_llm(self):
        """Setzt LLM Client auf"""
        if self.llm_client is None:
            try:
                # Versuche LiteLLM zu nutzen (bevorzugt für Gateway-Integration)
                import litellm
                self.llm_client = litellm
            except ImportError:
                try:
                    # Fallback zu OpenAI direkt
                    import openai
                    self.llm_client = openai
                except ImportError:
                    raise ImportError(
                        "Kein LLM Client verfügbar. Bitte installiere 'litellm' oder 'openai'."
                    )
    
    def _setup_tools(self, filtered_agents: Optional[List[str]] = None, package_type: Optional[str] = None):
        """
        Setzt Tools für LLM Orchestrator auf (MCP Best Practices)
        
        Args:
            filtered_agents: Gefilterte Agents (vom Intent Agent) - reduziert Tool-Auswahl
            package_type: Package Type für Filtering
        """
        # Verfügbare Agents als Tools für LLM
        self.available_agents = self._get_available_agents()
        
        # Filter Agents wenn Intent Agent Empfehlungen gibt
        agent_enum = list(self.available_agents.keys())
        if filtered_agents:
            # Nutze nur empfohlene Agents (Best Practice: Weniger Tools = bessere Entscheidungen)
            agent_enum = [a for a in filtered_agents if a in agent_enum]
            if not agent_enum:
                agent_enum = list(self.available_agents.keys())  # Fallback
        
        # Hole MCP Tools (alle Agents als Tools)
        mcp_tools = self.mcp_tool_registry.get_tools_for_orchestrator(
            package_type=package_type,
            filtered_agents=filtered_agents
        )
        
        # Konvertiere MCP Tools zu OpenAI Function Tools
        agent_tools = []
        for mcp_tool in mcp_tools:
            agent_tools.append({
                "type": "function",
                "function": {
                    "name": f"call_agent_{mcp_tool['metadata']['agent_name']}",
                    "description": mcp_tool["description"],
                    "parameters": mcp_tool["inputSchema"]
                }
            })
        
        # Basis-Tools (Routing, Escalation, Web Search)
        base_tools = [
            {
                "type": "function",
                "function": {
                    "name": "route_to_agent",
                    "description": "Routet Request zu passendem Agent basierend auf Intent und Kontext",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Name des Ziel-Agents",
                                "enum": agent_enum  # Gefilterte Liste!
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Begründung für Routing-Entscheidung"
                            },
                            "confidence": {
                                "type": "number",
                                "description": "Confidence-Level (0.0-1.0)",
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["agent_name", "reasoning", "confidence"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_human",
                    "description": "Eskaliert zu Human wenn nötig (bei komplexen Fällen, Sicherheitsbedenken, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Grund für Eskalation",
                                "enum": [
                                    "complex_query",
                                    "safety_concern",
                                    "emotional_distress",
                                    "user_request",
                                    "policy_violation"
                                ]
                            },
                            "priority": {
                                "type": "string",
                                "description": "Priorität",
                                "enum": ["low", "medium", "high", "urgent", "critical"]
                            },
                            "explanation": {
                                "type": "string",
                                "description": "Erklärung für Eskalation"
                            }
                        },
                        "required": ["reason", "priority", "explanation"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Suche im Internet nach aktuellen Informationen. Nutze für: Öffnungszeiten prüfen, aktuelle Events, externe Daten, Verifikation von Informationen.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Suchanfrage für Web-Suche"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Grund für Web-Suche (z.B. 'Öffnungszeiten verifizieren', 'Aktuelle Events prüfen')"
                            }
                        },
                        "required": ["query", "reason"]
                    }
                }
            }
        ]
        
        # Kombiniere: Basis-Tools + Agent-Tools (MCP Format)
        self.tools = base_tools + agent_tools
    
    def _get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Holt verfügbare Agents mit Beschreibungen"""
        agents = {}
        
        # Gastronomie-Agents
        agents.update({
            "gastronomy_supervisor_agent": {
                "description": "Gastronomie Supervisor - routet Gastro-Anfragen",
                "package": "gastronomy"
            },
            "restaurant_voice_host_agent": {
                "description": "Restaurant Voice Host - Reservierungen, Öffnungszeiten, allgemeine Infos",
                "package": "gastronomy"
            },
            "restaurant_takeout_order_agent": {
                "description": "Takeout Bestellungen - Bestellungen zum Mitnehmen aufnehmen",
                "package": "gastronomy"
            },
            "restaurant_menu_allergen_agent": {
                "description": "Allergen-Auskünfte - Allergene, Diäten, Menü-Infos",
                "package": "gastronomy"
            },
            "restaurant_events_catering_agent": {
                "description": "Events & Catering - Gruppenbuchungen, Catering-Anfragen",
                "package": "gastronomy"
            },
            "restaurant_reputation_agent": {
                "description": "Review-Management - Reviews verwalten und beantworten",
                "package": "gastronomy"
            },
        })
        
        # Praxis-Agents
        agents.update({
            "practice_supervisor_agent": {
                "description": "Praxis Supervisor - routet Praxis-Anfragen mit Safety-Check",
                "package": "practice"
            },
            "practice_phone_reception_agent": {
                "description": "Praxis Empfang - Termine, Öffnungszeiten, allgemeine Infos",
                "package": "practice"
            },
            "practice_appointment_reminder_agent": {
                "description": "Terminerinnerungen - No-Show-Reduktion, Reminder",
                "package": "practice"
            },
            "practice_patient_intake_forms_agent": {
                "description": "Patienten-Formulare - digitale Formulare, Anamnese",
                "package": "practice"
            },
            "practice_admin_requests_agent": {
                "description": "Admin-Anfragen - Rezepte, Überweisungen, AU",
                "package": "practice"
            },
            "healthcare_privacy_guard_agent": {
                "description": "Privacy Guard - DSGVO-Compliance, Schweigepflicht",
                "package": "practice"
            },
        })
        
        # Allgemeine Agents
        agents.update({
            "support_triage_agent": {
                "description": "Support Triage - allgemeine Support-Anfragen",
                "package": "general"
            },
            "support_resolution_agent": {
                "description": "Support Resolution - Beschwerden, Probleme lösen",
                "package": "general"
            },
        })
        
        return agents
    
    async     async def route(
        self,
        request: RoutingRequest
    ) -> RoutingResponse:
        """
        Routet Request intelligent mit LLM
        
        Args:
            request: Routing-Anfrage
        
        Returns:
            RoutingResponse mit intelligenter Routing-Entscheidung
        """
        # Rate Limiting prüfen
        rate_limit_result = self.rate_limiter.check_account_limit(request.account_id)
        if not rate_limit_result.allowed:
            # Rate Limit überschritten
            return RoutingResponse(
                target_agent="rate_limit_exceeded",
                agent_instance=None,
                reasoning=f"Rate Limit überschritten. Retry nach {rate_limit_result.retry_after} Sekunden.",
                confidence=1.0,
                metadata={
                    "rate_limit": {
                        "remaining": rate_limit_result.remaining,
                        "reset_at": rate_limit_result.reset_at.isoformat() if rate_limit_result.reset_at else None,
                        "retry_after": rate_limit_result.retry_after
                    }
                }
            )
        
        # Distributed Tracing
        with self.tracer.start_span("orchestrator.route", attributes={
            "account_id": request.account_id,
            "channel": request.channel
        }):
            with RequestTracker("llm_orchestrator", request.account_id):
                # 0. Language Detection & Translation (Multi-Language Support)
                detected_language = self.language_detector.detect(request.user_message)
                user_message = request.user_message
                
                # Übersetze falls nötig (zu Default-Language für bessere LLM-Performance)
                if detected_language.language != self.default_language and detected_language.language != Language.AUTO:
                    translation = self.translator.translate(
                        request.user_message,
                        target_language=self.default_language,
                        source_language=detected_language.language
                    )
                    user_message = translation.translated_text
                    request.user_message = user_message  # Update für weitere Verarbeitung
                
                # 0.5. Intent erkennen (SCHNELL mit Intent Agent) - filtert auch Agents!
                intent_result = self.intent_agent.detect_intent(
                    user_message=user_message,
                    account_id=request.account_id,
                    context=request.context
                )
                
                # 1. Package Manifest laden
                manifest = self.manifest_registry.get_manifest(request.account_id)
                
                # 1.5. Tools mit gefilterten Agents aktualisieren (Best Practice!)
                filtered_agents = intent_result.recommended_agents if intent_result.recommended_agents else None
                package_type = manifest.package_type.value if manifest else None
                self._setup_tools(filtered_agents=filtered_agents, package_type=package_type)
                
                # 2. Consent & Redaction prüfen
                consent_result = self._check_consent_and_redact(request, manifest)
                if not consent_result["allowed"]:
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
                        reasoning="Consent erforderlich",
                        confidence=1.0,
                        requires_handoff=True,
                        handoff_context=handoff
                    )
                
                # 3. LLM-basierte Routing-Entscheidung (mit gefilterten Agents!)
                routing_decision = await self._llm_route(
                    request=request,
                    manifest=manifest,
                    consent_result=consent_result,
                    intent_result=intent_result
                )
                
                # 4. Agent-Instanz holen
                agent_instance = self.agent_registry.get_agent(
                    routing_decision["agent_name"],
                    request.account_id
                )
                
                if not agent_instance:
                    # Fallback
                    return self._fallback_routing(request, manifest)
                
                # 5. Monitoring
                self.monitor.track_routing_decision(
                    account_id=request.account_id,
                    source_agent="llm_orchestrator",
                    target_agent=routing_decision["agent_name"],
                    intent=routing_decision.get("intent", "unknown"),
                    confidence=routing_decision["confidence"]
                )
                
                # 5.5. Real-time Metrics (async)
                try:
                    await self.real_time_monitor.send_metric(
                        RealTimeMetric(
                            name="orchestrator.routing",
                            value=1.0,
                            labels={
                                "target_agent": routing_decision["agent_name"],
                                "account_id": request.account_id
                            }
                        )
                    )
                except Exception as e:
                    logger.warning(f"Fehler beim Senden von Real-time Metric: {e}")
                
                # 5.6. Event Bus (async)
                try:
                    await self.event_bus.publish(
                        Event(
                            id=f"route_{request.account_id}_{datetime.now().timestamp()}",
                            type=EventType.ROUTING_DECISION,
                            payload={
                                "source_agent": "llm_orchestrator",
                                "target_agent": routing_decision["agent_name"],
                                "intent": routing_decision.get("intent", "unknown"),
                                "confidence": routing_decision["confidence"]
                            },
                            source="orchestrator",
                            account_id=request.account_id
                        )
                    )
                except Exception as e:
                    logger.warning(f"Fehler beim Publishen von Event: {e}")
                
                # 5.7. Cost Tracking (automatisch für LLM-Calls)
                # Schätze LLM-Kosten basierend auf Tokens (vereinfacht)
                # In Production: Echte Token-Counts von LLM Response
                estimated_cost = 0.001  # Beispiel: $0.001 pro Request
                self.cost_tracker.track_cost(
                    account_id=request.account_id,
                    cost_type=CostType.LLM_API,
                    amount=estimated_cost,
                    agent_name="llm_orchestrator",
                    metadata={"model": self.model}
                )
                
                # 5.8. Learning System - Automatisches Feedback-Sammeln
                try:
                    from apps.agents.core.agent_learning import get_learning_system, FeedbackType, FeedbackSource
                    learning = get_learning_system()
                    learning.collect_feedback(
                        agent_name=routing_decision["agent_name"],
                        feedback_type=FeedbackType.NEUTRAL,  # System-generated
                        source=FeedbackSource.SYSTEM,
                        context={
                            "routing_decision": routing_decision,
                            "intent": routing_decision.get("intent", "unknown"),
                            "confidence": routing_decision["confidence"],
                            "account_id": request.account_id
                        }
                    )
                except Exception as e:
                    logger.warning(f"Fehler beim automatischen Feedback-Sammeln: {e}")
                
                # 5.9. Workflow Auto-Creation - Erstellt automatisch Workflows
                try:
                    from apps.agents.core.workflow_auto_creation import get_workflow_auto_creator
                    workflow_creator = get_workflow_auto_creator()
                    workflow_id = await workflow_creator.create_workflow_for_routing(
                        routing_decision=routing_decision,
                        request_context={
                            "account_id": request.account_id,
                            "user_id": request.user_id,
                            "channel": request.channel,
                            "conversation_id": request.conversation_id
                        }
                    )
                    if workflow_id:
                        # Füge Workflow ID zu Metadata hinzu
                        if "metadata" not in locals():
                            metadata = {}
                        metadata["workflow_id"] = workflow_id
                        logger.info(f"Automatischer Workflow erstellt: {workflow_id}")
                except Exception as e:
                    logger.warning(f"Fehler bei Workflow Auto-Creation: {e}")
                
                return RoutingResponse(
                    target_agent=routing_decision["agent_name"],
                    agent_instance=agent_instance,
                    reasoning=routing_decision["reasoning"],
                    confidence=routing_decision["confidence"],
                    redacted_message=consent_result.get("redacted_message"),
                    metadata={
                        "intent": routing_decision.get("intent"),
                        "package_type": manifest.package_type.value if manifest else None,
                        "llm_model": self.model
                    }
                )
    
    async def _llm_route(
        self,
        request: RoutingRequest,
        manifest: Optional[Any],
        consent_result: Dict[str, Any],
        intent_result: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        LLM-basierte Routing-Entscheidung
        
        Returns:
            Dict mit agent_name, reasoning, confidence
        """
        # System Prompt für Orchestrator (Best Practices)
        system_prompt = self._build_orchestrator_prompt(manifest)
        
        # User Message mit Kontext (Best Practices)
        user_message = self._build_routing_message(request, manifest, consent_result)
        
        # Füge Intent-Info hinzu (wenn verfügbar)
        if intent_result:
            user_message += f"\n\n[Intent-Erkennung]: {intent_result.intent.value} (Confidence: {intent_result.confidence:.2f})"
            if intent_result.reasoning:
                user_message += f"\n[Intent-Begründung]: {intent_result.reasoning}"
        
        # LLM Call mit Tools (mit Error Handling & Retry)
        @retry_with_backoff(retry_on=[Exception])
        @graceful_degradation(fallback_value={"agent_name": "support_triage_agent", "reasoning": "Fallback nach Fehler", "confidence": 0.5})
        def _make_llm_call():
            if hasattr(self.llm_client, 'chat') and hasattr(self.llm_client.chat, 'completions'):
                # OpenAI direkt
                return self.llm_client.chat.completions.create(
                    model=self._get_available_model(),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.1,  # Niedrig für konsistente Entscheidungen
                    max_tokens=500
                )
            else:
                # LiteLLM
                return self.llm_client.completion(
                    model=self._get_available_model(),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.1,
                    max_tokens=500
                )
        
        try:
            response = _make_llm_call()
            
            # Parse Tool Calls (kann mehrere sein, z.B. web_search dann route_to_agent)
            message = response.choices[0].message
            
            if message.tool_calls:
                # Verarbeite alle Tool Calls (können mehrere sein)
                web_search_results = None
                final_decision = None
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    if function_name == "web_search":
                        # Web Search ausführen (async)
                        web_search_results = await self._execute_web_search(
                            query=arguments["query"],
                            reason=arguments["reason"]
                        )
                        
                        # Füge Suchergebnisse zu User Message hinzu für nächsten LLM-Call
                        if web_search_results and web_search_results.get("results"):
                            # Erweitere User Message mit Suchergebnissen
                            user_message += f"\n\n[Web Search Results für '{arguments['query']}']:\n"
                            for i, result in enumerate(web_search_results["results"][:3], 1):
                                user_message += f"{i}. {result.get('title', '')}: {result.get('snippet', '')}\n"
                        
                        # Mache zweiten LLM-Call mit Suchergebnissen
                        if web_search_results:
                            # Erneuter LLM-Call mit Suchergebnissen
                            if hasattr(self.llm_client, 'chat') and hasattr(self.llm_client.chat, 'completions'):
                                follow_up_response = self.llm_client.chat.completions.create(
                                model=self._get_available_model(),
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_message},
                                    {"role": "assistant", "content": message.content},
                                    {"role": "user", "content": f"Web Search Results: {json.dumps(web_search_results, ensure_ascii=False)}. Jetzt routiere basierend auf diesen Informationen."}
                                ],
                                tools=[t for t in self.tools if t["function"]["name"] != "web_search"],  # Web Search nicht nochmal
                                tool_choice="auto",
                                temperature=0.1,
                                max_tokens=500
                            )
                            
                            # Parse Follow-up Tool Call
                            follow_up_message = follow_up_response.choices[0].message
                            if follow_up_message.tool_calls:
                                tool_call = follow_up_message.tool_calls[0]
                                function_name = tool_call.function.name
                                arguments = json.loads(tool_call.function.arguments)
                                
                                if function_name == "route_to_agent":
                                    return {
                                        "agent_name": arguments["agent_name"],
                                        "reasoning": f"{arguments['reasoning']} (Web Search: {web_search_results.get('query', '')})",
                                        "confidence": arguments["confidence"],
                                        "intent": self._extract_intent_from_reasoning(arguments["reasoning"]),
                                        "web_search_used": True
                                    }
                        
                    elif function_name == "route_to_agent":
                        final_decision = {
                            "agent_name": arguments["agent_name"],
                            "reasoning": arguments["reasoning"],
                            "confidence": arguments["confidence"],
                            "intent": self._extract_intent_from_reasoning(arguments["reasoning"]),
                            "web_search_used": web_search_results is not None
                        }
                        
                    elif function_name == "escalate_to_human":
                        # Handoff
                        handoff = self.handoff_protocol.should_handoff(
                            account_id=request.account_id,
                            user_id=request.user_id,
                            channel=request.channel,
                            conversation_id=request.conversation_id or "unknown",
                            reason=HandoffReason[arguments["reason"].upper()],
                            context={"explanation": arguments["explanation"]}
                        )
                        final_decision = {
                            "agent_name": "handoff",
                            "reasoning": arguments["explanation"],
                            "confidence": 1.0,
                            "handoff": handoff
                        }
                
                if final_decision:
                    return final_decision
            
            # Fallback wenn kein Tool Call
            return self._fallback_routing_logic(request, manifest)
            
        except Exception as e:
            # Error Handling mit Error Handler
            error_category = self.error_handler.categorize_error(e)
            logger.error(f"Fehler bei LLM Routing: {e} (Kategorie: {error_category.value})")
            
            # Graceful Degradation: Fallback zu einfacherem Routing
            return self._fallback_routing_logic(request, manifest)
    
    async def _execute_web_search(
        self,
        query: str,
        reason: str
    ) -> Optional[Dict[str, Any]]:
        """
        Führt Web-Suche aus
        
        Returns:
            Dict mit Suchergebnissen
        """
        try:
            # Nutze Web Search Tool (vollständig implementiert)
            result = await self.web_search_tool.search(query, max_results=5)
            
            # Füge Reason hinzu
            result["reason"] = reason
            
            # Track Cost für Web Search
            self.cost_tracker.track_cost(
                account_id="system",
                cost_type=CostType.NETWORK,  # Network Cost für Web Search
                amount=0.0001,  # Beispiel: $0.0001 pro Search
                agent_name="web_search_tool",
                metadata={"query": query, "provider": result.get("provider")}
            )
            
            return result
        except Exception as e:
            # Error Handling für Web Search
            error_category = self.error_handler.categorize_error(e)
            logger.warning(f"Fehler bei Web Search: {e} (Kategorie: {error_category.value})")
            return None
    
    def _get_available_model(self) -> str:
        """Holt verfügbares Modell (mit Fallback)"""
        # Versuche Modell aus ENV oder Default
        model = os.getenv("ORCHESTRATOR_MODEL", self.model)
        
        # TODO: Prüfe Modell-Verfügbarkeit und nutze Fallback-Kette
        # Für jetzt: Nutze Modell aus ENV oder Default
        return model
    
    def _build_orchestrator_prompt(self, manifest: Optional[Any]) -> str:
        """Baut System Prompt für Orchestrator (nutzt Best Practices)"""
        from apps.agents.core.prompt_templates import OrchestratorPromptBuilder
        
        package_type = manifest.package_type.value if manifest else None
        return OrchestratorPromptBuilder.build_system_prompt(
            available_agents=self.available_agents,
            package_type=package_type
        )
    
    def _build_routing_message(
        self,
        request: RoutingRequest,
        manifest: Optional[Any],
        consent_result: Dict[str, Any]
    ) -> str:
        """Baut User Message für Routing (nutzt Best Practices)"""
        from apps.agents.core.prompt_templates import OrchestratorPromptBuilder
        
        package_type = manifest.package_type.value if manifest else None
        return OrchestratorPromptBuilder.build_routing_message(
            user_message=consent_result.get('redacted_message', request.user_message),
            channel=request.channel,
            package_type=package_type,
            conversation_history=request.conversation_history,
            context=request.context
        )
    
    def _extract_intent_from_reasoning(self, reasoning: str) -> str:
        """Extrahiert Intent aus Reasoning (für Monitoring)"""
        reasoning_lower = reasoning.lower()
        
        intents = {
            "reservierung": "reservation",
            "bestellung": "takeout_order",
            "termin": "appointment",
            "rezept": "prescription",
            "allergen": "allergen_query",
            "event": "event_catering",
        }
        
        for keyword, intent in intents.items():
            if keyword in reasoning_lower:
                return intent
        
        return "unknown"
    
    def _check_consent_and_redact(
        self,
        request: RoutingRequest,
        manifest: Optional[Any]
    ) -> Dict[str, Any]:
        """Prüft Consent und redactiert Content"""
        if not manifest:
            return {"allowed": True, "redacted_message": request.user_message}
        
        redacted, categories = self.consent_gateway.redact_content(
            content=request.user_message,
            account_id=request.account_id,
            user_id=request.user_id,
            require_consent=manifest.policies.require_consent
        )
        
        return {
            "allowed": True,
            "redacted_message": redacted,
            "redacted_categories": categories
        }
    
    def _fallback_routing_logic(
        self,
        request: RoutingRequest,
        manifest: Optional[Any]
    ) -> Dict[str, Any]:
        """Fallback-Routing-Logik (wenn LLM fehlschlägt)"""
        if manifest:
            if manifest.package_type == PackageType.GASTRONOMY:
                return {
                    "agent_name": "gastronomy_supervisor_agent",
                    "reasoning": "Fallback: Gastronomie Supervisor",
                    "confidence": 0.5
                }
            elif manifest.package_type == PackageType.PRACTICE:
                return {
                    "agent_name": "practice_supervisor_agent",
                    "reasoning": "Fallback: Praxis Supervisor",
                    "confidence": 0.5
                }
        
        return {
            "agent_name": "support_triage_agent",
            "reasoning": "Fallback: Support Triage",
            "confidence": 0.3
        }
    
    def _fallback_routing(
        self,
        request: RoutingRequest,
        manifest: Optional[Any]
    ) -> RoutingResponse:
        """Fallback-Routing"""
        fallback = self._fallback_routing_logic(request, manifest)
        agent_instance = self.agent_registry.get_agent(
            fallback["agent_name"],
            request.account_id
        )
        
        return RoutingResponse(
            target_agent=fallback["agent_name"],
            agent_instance=agent_instance,
            reasoning=fallback["reasoning"],
            confidence=fallback["confidence"],
            metadata={"fallback": True}
        )


def get_llm_orchestrator(llm_client=None) -> 'LLMOrchestratorAgent':
    """Holt globale LLM Orchestrator-Instanz"""
    global _global_llm_orchestrator
    if _global_llm_orchestrator is None:
        _global_llm_orchestrator = LLMOrchestratorAgent(llm_client=llm_client)
    return _global_llm_orchestrator
