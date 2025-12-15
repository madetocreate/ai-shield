"""
Agent Registry - Zentrale Registrierung aller Agents

Ermöglicht Dependency Injection und zentrale Agent-Verwaltung.
"""

from typing import Dict, Optional, Any, Type, Callable
from dataclasses import dataclass
import importlib


@dataclass
class AgentConfig:
    """Konfiguration für einen Agent"""
    agent_class: Type
    dependencies: Dict[str, str] = None  # dependency_name -> agent_name
    enabled: bool = True
    config: Dict[str, Any] = None


class AgentRegistry:
    """
    Zentrale Registry für alle Agents
    
    Ermöglicht:
    - Zentrale Registrierung
    - Dependency Injection
    - Lazy Loading
    - Agent-Instanziierung mit Dependencies
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentConfig] = {}
        self._instances: Dict[str, Any] = {}  # Cache für Instanzen
    
    def register(
        self,
        agent_name: str,
        agent_class: Type,
        dependencies: Optional[Dict[str, str]] = None,
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Registriert einen Agent
        
        Args:
            agent_name: Name des Agents
            agent_class: Python-Klasse des Agents
            dependencies: Mapping von dependency_name zu agent_name
            enabled: Ob Agent aktiviert ist
            config: Zusätzliche Konfiguration
        """
        self._agents[agent_name] = AgentConfig(
            agent_class=agent_class,
            dependencies=dependencies or {},
            enabled=enabled,
            config=config or {}
        )
    
    def get_agent(
        self,
        agent_name: str,
        account_id: str,
        **kwargs
    ) -> Optional[Any]:
        """
        Holt Agent-Instanz mit Dependency Injection
        
        Args:
            agent_name: Name des Agents
            account_id: Account-ID
            **kwargs: Zusätzliche Parameter für Agent-Initialisierung
        
        Returns:
            Agent-Instanz oder None
        """
        if agent_name not in self._agents:
            return None
        
        config = self._agents[agent_name]
        
        if not config.enabled:
            return None
        
        # Cache prüfen
        cache_key = f"{agent_name}:{account_id}"
        if cache_key in self._instances:
            return self._instances[cache_key]
        
        # Dependencies auflösen
        dependency_instances = {}
        for dep_name, dep_agent_name in config.dependencies.items():
            dep_instance = self.get_agent(dep_agent_name, account_id, **kwargs)
            if dep_instance:
                dependency_instances[dep_name] = dep_instance
        
        # Agent instanziieren
        try:
            # Versuche account_id als ersten Parameter
            if 'account_id' in kwargs:
                instance = config.agent_class(account_id=account_id, **dependency_instances, **kwargs)
            else:
                instance = config.agent_class(account_id, **dependency_instances, **kwargs)
            
            # Cache speichern
            self._instances[cache_key] = instance
            return instance
        except Exception as e:
            print(f"Fehler beim Instanziieren von {agent_name}: {e}")
            return None
    
    def is_registered(self, agent_name: str) -> bool:
        """Prüft ob Agent registriert ist"""
        return agent_name in self._agents
    
    def is_enabled(self, agent_name: str) -> bool:
        """Prüft ob Agent aktiviert ist"""
        if agent_name not in self._agents:
            return False
        return self._agents[agent_name].enabled
    
    def list_agents(self) -> list[str]:
        """Listet alle registrierten Agents"""
        return list(self._agents.keys())
    
    def clear_cache(self, account_id: Optional[str] = None):
        """Löscht Agent-Cache"""
        if account_id:
            keys_to_remove = [k for k in self._instances.keys() if k.endswith(f":{account_id}")]
            for key in keys_to_remove:
                del self._instances[key]
        else:
            self._instances.clear()


# Globale Registry-Instanz
_global_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Holt globale Agent-Registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
        _register_all_agents(_global_registry)
    return _global_registry


def _register_all_agents(registry: AgentRegistry):
    """Registriert alle verfügbaren Agents"""
    # Gastronomie-Agents
    try:
        from apps.agents.gastronomy import (
            GastronomySupervisorAgent,
            RestaurantVoiceHostAgent,
            RestaurantMenuAllergenAgent,
            RestaurantTakeoutOrderAgent,
            RestaurantReputationAgent,
            RestaurantEventsCateringAgent,
            # V2 Agents
            RestaurantShiftStaffingAgent,
            RestaurantInventoryProcurementAgent,
            RestaurantDailyOpsReportAgent,
        )
        
        registry.register("gastronomy_supervisor_agent", GastronomySupervisorAgent)
        registry.register("restaurant_voice_host_agent", RestaurantVoiceHostAgent, {
            "integration_agent": "integration_agent"
        })
        registry.register("restaurant_menu_allergen_agent", RestaurantMenuAllergenAgent, {
            "knowledge_base_agent": "knowledge_base_agent",
            "document_intelligence_agent": "document_intelligence_agent"
        })
        registry.register("restaurant_takeout_order_agent", RestaurantTakeoutOrderAgent, {
            "integration_agent": "integration_agent"
        })
        registry.register("restaurant_reputation_agent", RestaurantReputationAgent, {
            "integration_agent": "integration_agent",
            "marketing_execution_agent": "marketing_execution_agent"
        })
        registry.register("restaurant_events_catering_agent", RestaurantEventsCateringAgent, {
            "crm_agent": "crm_agent",
            "proposal_agent": "proposal_agent",
            "followup_agent": "followup_agent",
            "personalization_agent": "personalization_agent"
        })
        # V2 Agents
        registry.register("restaurant_shift_staffing_agent", RestaurantShiftStaffingAgent, {
            "integration_agent": "integration_agent",
            "communications_supervisor": "communications_supervisor"
        })
        registry.register("restaurant_inventory_procurement_agent", RestaurantInventoryProcurementAgent, {
            "integration_agent": "integration_agent"
        })
        registry.register("restaurant_daily_ops_report_agent", RestaurantDailyOpsReportAgent, {
            "integration_agent": "integration_agent",
            "restaurant_reputation_agent": "restaurant_reputation_agent"
        })
    except ImportError as e:
        print(f"Fehler beim Importieren von Gastronomie-Agents: {e}")
    
    # Praxis-Agents
    try:
        from apps.agents.practice import (
            PracticeSupervisorAgent,
            PracticePhoneReceptionAgent,
            PracticeAppointmentReminderAgent,
            PracticePatientIntakeFormsAgent,
            PracticeAdminRequestsAgent,
            HealthcarePrivacyGuardAgent,
            # V2 Agents
            PracticeClinicalDocumentationAgent,
            PracticeBillingInsuranceAgent,
            PracticeDocumentInboxAgent,
        )
        
        registry.register("practice_supervisor_agent", PracticeSupervisorAgent)
        registry.register("practice_phone_reception_agent", PracticePhoneReceptionAgent, {
            "integration_agent": "integration_agent",
            "healthcare_privacy_guard": "healthcare_privacy_guard_agent"
        })
        registry.register("practice_appointment_reminder_agent", PracticeAppointmentReminderAgent, {
            "integration_agent": "integration_agent",
            "communications_supervisor": "communications_supervisor"
        })
        registry.register("practice_patient_intake_forms_agent", PracticePatientIntakeFormsAgent, {
            "document_intelligence_agent": "document_intelligence_agent",
            "integration_agent": "integration_agent",
            "communications_supervisor": "communications_supervisor"
        })
        registry.register("practice_admin_requests_agent", PracticeAdminRequestsAgent, {
            "integration_agent": "integration_agent",
            "communications_supervisor": "communications_supervisor"
        })
        registry.register("healthcare_privacy_guard_agent", HealthcarePrivacyGuardAgent, {
            "consent_gateway": "consent_and_redaction_gateway"
        })
        # V2 Agents
        registry.register("practice_clinical_documentation_agent", PracticeClinicalDocumentationAgent, {
            "summarizer_agent": "summarizer_agent",
            "integration_agent": "integration_agent"
        })
        registry.register("practice_billing_insurance_agent", PracticeBillingInsuranceAgent, {
            "integration_agent": "integration_agent",
            "communications_supervisor": "communications_supervisor"
        })
        registry.register("practice_document_inbox_agent", PracticeDocumentInboxAgent, {
            "document_intelligence_agent": "document_intelligence_agent",
            "integration_agent": "integration_agent"
        })
    except ImportError as e:
        print(f"Fehler beim Importieren von Praxis-Agents: {e}")
