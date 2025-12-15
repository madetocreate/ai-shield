"""
Tests für Global Orchestrator
"""

import pytest
from apps.agents.core.global_orchestrator_agent import (
    GlobalOrchestratorAgent,
    RoutingRequest,
    get_orchestrator
)
from apps.agents.shared.vertical_package_manifest import (
    VerticalPackageManifest,
    PackageType,
    PolicyConfig,
    get_registry as get_manifest_registry
)


class TestGlobalOrchestratorAgent:
    """Tests für Global Orchestrator Agent"""
    
    def test_init(self):
        """Test Orchestrator-Initialisierung"""
        orchestrator = GlobalOrchestratorAgent()
        assert orchestrator.manifest_registry is not None
        assert orchestrator.agent_registry is not None
        assert orchestrator.handoff_protocol is not None
    
    def test_route_gastronomy(self):
        """Test Routing für Gastronomie-Paket"""
        # Manifest erstellen
        manifest_registry = get_manifest_registry()
        manifest = VerticalPackageManifest(
            package_type=PackageType.GASTRONOMY,
            account_id="test-restaurant",
            enabled_agents=[
                "gastronomy_supervisor_agent",
                "restaurant_voice_host_agent"
            ],
            policies=PolicyConfig(require_consent=False)
        )
        manifest_registry.save_manifest(manifest)
        
        # Orchestrator testen
        orchestrator = GlobalOrchestratorAgent()
        request = RoutingRequest(
            account_id="test-restaurant",
            user_message="Ich möchte einen Tisch reservieren",
            channel="phone"
        )
        
        response = orchestrator.route(request)
        
        assert response.target_agent in [
            "restaurant_voice_host_agent",
            "gastronomy_supervisor_agent"
        ]
        assert response.metadata is not None
        assert response.metadata.get("package_type") == "gastronomy"
    
    def test_route_practice(self):
        """Test Routing für Praxis-Paket"""
        # Manifest erstellen
        manifest_registry = get_manifest_registry()
        manifest = VerticalPackageManifest(
            package_type=PackageType.PRACTICE,
            account_id="test-praxis",
            enabled_agents=[
                "practice_supervisor_agent",
                "practice_phone_reception_agent"
            ],
            policies=PolicyConfig(require_consent=False)
        )
        manifest_registry.save_manifest(manifest)
        
        # Orchestrator testen
        orchestrator = GlobalOrchestratorAgent()
        request = RoutingRequest(
            account_id="test-praxis",
            user_message="Ich möchte einen Termin vereinbaren",
            channel="phone"
        )
        
        response = orchestrator.route(request)
        
        assert response.target_agent in [
            "practice_phone_reception_agent",
            "practice_supervisor_agent"
        ]
        assert response.metadata is not None
        assert response.metadata.get("package_type") == "practice"
    
    def test_fallback_routing(self):
        """Test Fallback-Routing ohne Manifest"""
        orchestrator = GlobalOrchestratorAgent()
        request = RoutingRequest(
            account_id="unknown-account",
            user_message="Hallo",
            channel="phone"
        )
        
        response = orchestrator.route(request)
        
        # Sollte Fallback verwenden
        assert response.metadata is not None
        assert response.metadata.get("fallback") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
