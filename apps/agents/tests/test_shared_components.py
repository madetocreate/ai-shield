"""
Tests für Shared Components
"""

import pytest
from datetime import datetime, timedelta
from apps.agents.shared.vertical_package_manifest import (
    VerticalPackageManifest,
    PackageType,
    IntegrationConfig,
    PolicyConfig,
    get_registry
)
from apps.agents.shared.consent_and_redaction_gateway import (
    get_gateway,
    DataCategory,
    ConsentStatus
)
from apps.agents.shared.handoff_to_human_protocol import (
    get_protocol,
    HandoffReason,
    HandoffPriority
)


class TestVerticalPackageManifest:
    """Tests für Vertical Package Manifest"""
    
    def test_create_manifest(self):
        """Test Manifest erstellen"""
        manifest = VerticalPackageManifest(
            package_type=PackageType.GASTRONOMY,
            account_id="test-restaurant",
            enabled_agents=["gastronomy_supervisor_agent"],
            policies=PolicyConfig(preset="public_website")
        )
        
        assert manifest.package_type == PackageType.GASTRONOMY
        assert manifest.account_id == "test-restaurant"
        assert "gastronomy_supervisor_agent" in manifest.enabled_agents
    
    def test_is_agent_enabled(self):
        """Test Agent-Aktivierung prüfen"""
        manifest = VerticalPackageManifest(
            package_type=PackageType.GASTRONOMY,
            account_id="test-restaurant",
            enabled_agents=["gastronomy_supervisor_agent"]
        )
        
        assert manifest.is_agent_enabled("gastronomy_supervisor_agent") is True
        assert manifest.is_agent_enabled("unknown_agent") is False
    
    def test_get_integration(self):
        """Test Integration abrufen"""
        manifest = VerticalPackageManifest(
            package_type=PackageType.GASTRONOMY,
            account_id="test-restaurant",
            integrations=[
                IntegrationConfig(
                    integration_id="opentable",
                    enabled=True,
                    config={"api_key": "test"}
                )
            ]
        )
        
        integration = manifest.get_integration("opentable")
        assert integration is not None
        assert integration.integration_id == "opentable"
        assert integration.enabled is True
    
    def test_to_dict_from_dict(self):
        """Test Serialisierung"""
        manifest = VerticalPackageManifest(
            package_type=PackageType.GASTRONOMY,
            account_id="test-restaurant",
            enabled_agents=["gastronomy_supervisor_agent"]
        )
        
        data = manifest.to_dict()
        restored = VerticalPackageManifest.from_dict(data)
        
        assert restored.package_type == manifest.package_type
        assert restored.account_id == manifest.account_id


class TestConsentAndRedactionGateway:
    """Tests für Consent and Redaction Gateway"""
    
    def test_grant_consent(self):
        """Test Consent erteilen"""
        gateway = get_gateway()
        consent = gateway.grant_consent(
            account_id="test-account",
            user_id="user-123",
            category=DataCategory.PII,
            expires_in_days=90
        )
        
        assert consent.status == ConsentStatus.GRANTED
        assert consent.account_id == "test-account"
        assert consent.is_valid() is True
    
    def test_check_consent(self):
        """Test Consent prüfen"""
        gateway = get_gateway()
        
        # Consent erteilen
        gateway.grant_consent(
            account_id="test-account",
            user_id="user-123",
            category=DataCategory.PII
        )
        
        # Prüfen
        has_consent = gateway.check_consent(
            account_id="test-account",
            user_id="user-123",
            category=DataCategory.PII
        )
        
        assert has_consent is True
    
    def test_redact_content(self):
        """Test Content redactieren"""
        gateway = get_gateway()
        
        content = "Meine E-Mail ist max@example.com und Telefon 0123456789"
        redacted, categories = gateway.redact_content(
            content=content,
            account_id="test-account",
            require_consent=False
        )
        
        assert "[EMAIL]" in redacted or "[PHONE]" in redacted
        assert len(categories) > 0
    
    def test_set_retention_policy(self):
        """Test Retention-Policy setzen"""
        gateway = get_gateway()
        gateway.set_retention_policy("test-account", days=365)
        
        # Prüfen ob Policy gesetzt wurde
        assert "test-account" in gateway.retention_policies


class TestHandoffToHumanProtocol:
    """Tests für Handoff to Human Protocol"""
    
    def test_should_handoff_safety_concern(self):
        """Test Handoff bei Safety-Concern"""
        protocol = get_protocol()
        handoff = protocol.should_handoff(
            account_id="test-account",
            user_id="user-123",
            channel="phone",
            conversation_id="conv-123",
            reason=HandoffReason.SAFETY_CONCERN,
            context={"urgency": "high"}
        )
        
        assert handoff is not None
        assert handoff.priority == HandoffPriority.CRITICAL
        assert handoff.method.value == "live_transfer"
    
    def test_get_pending_handoffs(self):
        """Test ausstehende Handoffs abrufen"""
        protocol = get_protocol()
        
        # Handoff erstellen
        protocol.should_handoff(
            account_id="test-account",
            user_id="user-123",
            channel="phone",
            conversation_id="conv-123",
            reason=HandoffReason.SAFETY_CONCERN
        )
        
        # Abrufen
        pending = protocol.get_pending_handoffs(
            account_id="test-account",
            priority=HandoffPriority.CRITICAL
        )
        
        assert len(pending) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
