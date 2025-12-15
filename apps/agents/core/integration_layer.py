"""
Integration Layer - Verbindet Agents mit bestehendem System

Ermöglicht:
- Integration mit Communications Supervisor
- Integration mit Integration Agent
- Integration mit Knowledge Base
- Integration mit CRM
- Integration mit Monitoring
"""

from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Konfiguration für Integration"""
    name: str
    enabled: bool = True
    adapter: Optional[Callable] = None
    config: Dict[str, Any] = None


class IntegrationLayer:
    """
    Integration Layer für Agent-System
    
    Stellt Adapter für bestehende System-Komponenten bereit.
    """
    
    def __init__(self):
        self.integrations: Dict[str, IntegrationConfig] = {}
        self._setup_default_integrations()
    
    def _setup_default_integrations(self):
        """Setzt Standard-Integrationen auf"""
        # Nutze echte Integrationen falls verfügbar, sonst Mocks
        try:
            from apps.agents.core.real_integrations import (
                get_communications_supervisor,
                get_integration_agent,
                get_knowledge_base_agent,
                get_crm_agent
            )
            
            # Echte Integrationen
            self.register_integration(
                "communications_supervisor",
                get_communications_supervisor(),
                enabled=True
            )
            self.register_integration(
                "integration_agent",
                get_integration_agent(),
                enabled=True
            )
            self.register_integration(
                "knowledge_base_agent",
                get_knowledge_base_agent(),
                enabled=True
            )
            self.register_integration(
                "crm_agent",
                get_crm_agent(),
                enabled=True
            )
            logger.info("Echte Integrationen geladen")
        except Exception as e:
            logger.warning(f"Echte Integrationen nicht verfügbar, nutze Mocks: {e}")
            # Fallback zu Mocks
            self.register_integration("communications_supervisor", self._mock_communications)
            self.register_integration("integration_agent", self._mock_integration)
            self.register_integration("knowledge_base_agent", self._mock_knowledge_base)
            self.register_integration("crm_agent", self._mock_crm)
    
    def register_integration(
        self,
        name: str,
        adapter: Callable,
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """Registriert Integration"""
        self.integrations[name] = IntegrationConfig(
            name=name,
            enabled=enabled,
            adapter=adapter,
            config=config or {}
        )
        logger.info(f"Integration registriert: {name}")
    
    def get_integration(self, name: str) -> Optional[Callable]:
        """Holt Integration-Adapter"""
        integration = self.integrations.get(name)
        if not integration or not integration.enabled:
            return None
        return integration.adapter
    
    def _mock_communications(self, *args, **kwargs):
        """Mock Communications Supervisor"""
        logger.warning("Mock Communications Supervisor verwendet - echte Integration erforderlich")
        return {"status": "mock", "message": "Mock implementation"}
    
    def _mock_integration(self, *args, **kwargs):
        """Mock Integration Agent"""
        logger.warning("Mock Integration Agent verwendet - echte Integration erforderlich")
        return {"status": "mock", "message": "Mock implementation"}
    
    def _mock_knowledge_base(self, *args, **kwargs):
        """Mock Knowledge Base Agent"""
        logger.warning("Mock Knowledge Base Agent verwendet - echte Integration erforderlich")
        return {"status": "mock", "message": "Mock implementation"}
    
    def _mock_crm(self, *args, **kwargs):
        """Mock CRM Agent"""
        logger.warning("Mock CRM Agent verwendet - echte Integration erforderlich")
        return {"status": "mock", "message": "Mock implementation"}


# Globale Integration Layer-Instanz
_global_integration_layer: Optional[IntegrationLayer] = None


def get_integration_layer() -> IntegrationLayer:
    """Holt globale Integration Layer-Instanz"""
    global _global_integration_layer
    if _global_integration_layer is None:
        _global_integration_layer = IntegrationLayer()
    return _global_integration_layer


def connect_to_existing_system(
    communications_supervisor=None,
    integration_agent=None,
    knowledge_base_agent=None,
    crm_agent=None
):
    """
    Verbindet Integration Layer mit bestehendem System
    
    Args:
        communications_supervisor: Echter Communications Supervisor (optional, nutzt Default falls None)
        integration_agent: Echter Integration Agent (optional, nutzt Default falls None)
        knowledge_base_agent: Echter Knowledge Base Agent (optional, nutzt Default falls None)
        crm_agent: Echter CRM Agent (optional, nutzt Default falls None)
    """
    layer = get_integration_layer()
    
    # Nutze echte Integrationen (aus real_integrations.py)
    if communications_supervisor is None:
        try:
            from apps.agents.core.real_integrations import get_communications_supervisor
            communications_supervisor = get_communications_supervisor()
        except Exception as e:
            logger.warning(f"Konnte Communications Supervisor nicht laden: {e}")
    
    if integration_agent is None:
        try:
            from apps.agents.core.real_integrations import get_integration_agent
            integration_agent = get_integration_agent()
        except Exception as e:
            logger.warning(f"Konnte Integration Agent nicht laden: {e}")
    
    if knowledge_base_agent is None:
        try:
            from apps.agents.core.real_integrations import get_knowledge_base_agent
            knowledge_base_agent = get_knowledge_base_agent()
        except Exception as e:
            logger.warning(f"Konnte Knowledge Base Agent nicht laden: {e}")
    
    if crm_agent is None:
        try:
            from apps.agents.core.real_integrations import get_crm_agent
            crm_agent = get_crm_agent()
        except Exception as e:
            logger.warning(f"Konnte CRM Agent nicht laden: {e}")
    
    # Registriere Integrationen
    if communications_supervisor:
        layer.register_integration(
            "communications_supervisor",
            communications_supervisor,
            enabled=True
        )
        logger.info("Communications Supervisor verbunden")
    
    if integration_agent:
        layer.register_integration(
            "integration_agent",
            integration_agent,
            enabled=True
        )
        logger.info("Integration Agent verbunden")
    
    if knowledge_base_agent:
        layer.register_integration(
            "knowledge_base_agent",
            knowledge_base_agent,
            enabled=True
        )
        logger.info("Knowledge Base Agent verbunden")
    
    if crm_agent:
        layer.register_integration(
            "crm_agent",
            crm_agent,
            enabled=True
        )
        logger.info("CRM Agent verbunden")
