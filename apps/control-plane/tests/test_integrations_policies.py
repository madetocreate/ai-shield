"""
Tests for integrations policies module.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add control-plane/app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from integrations.policies import get_default_scopes
from integrations.types import Provider


def test_default_scopes_env_override():
    """Test that ENV variable overrides default scopes."""
    # Test with GOOGLE provider
    with patch.dict(os.environ, {"INTEGRATIONS_DEFAULT_SCOPES_GOOGLE": "calendar.read,calendar.write"}):
        scopes = get_default_scopes(Provider.GOOGLE)
        assert scopes == ["calendar.read", "calendar.write"]
    
    # Test with JSON array format
    with patch.dict(os.environ, {"INTEGRATIONS_DEFAULT_SCOPES_GOOGLE": '["calendar.read","calendar.write"]'}):
        scopes = get_default_scopes(Provider.GOOGLE)
        assert scopes == ["calendar.read", "calendar.write"]
    
    # Test with comma-separated string (with spaces)
    with patch.dict(os.environ, {"INTEGRATIONS_DEFAULT_SCOPES_SLACK": "channels:read, channels:write, chat:write"}):
        scopes = get_default_scopes(Provider.SLACK)
        assert scopes == ["channels:read", "channels:write", "chat:write"]
    
    # Test deduplication
    with patch.dict(os.environ, {"INTEGRATIONS_DEFAULT_SCOPES_HUBSPOT": "contacts.read,contacts.read,contacts.write"}):
        scopes = get_default_scopes(Provider.HUBSPOT)
        assert scopes == ["contacts.read", "contacts.write"]
    
    # Test fallback to defaults when ENV not set
    with patch.dict(os.environ, {}, clear=True):
        scopes = get_default_scopes(Provider.GOOGLE)
        assert scopes == ["calendar.readonly"]
    
    # Test provider.name is used (not provider.value)
    # MICROSOFT_365 has value "microsoft-365" but name "MICROSOFT_365"
    with patch.dict(os.environ, {"INTEGRATIONS_DEFAULT_SCOPES_MICROSOFT_365": "Calendars.Read"}):
        scopes = get_default_scopes(Provider.MICROSOFT_365)
        assert scopes == ["Calendars.Read"]


def test_default_scopes_fallback():
    """Test fallback to defaults for providers without ENV override."""
    with patch.dict(os.environ, {}, clear=True):
        # Test various providers
        assert get_default_scopes(Provider.GOOGLE_DRIVE) == ["drive.readonly"]
        assert get_default_scopes(Provider.SHOPIFY) == ["read_orders", "read_customers"]
        assert get_default_scopes(Provider.CALENDLY) == ["read"]
        assert get_default_scopes(Provider.ZOOM) == ["meeting:read", "meeting:write"]
        assert get_default_scopes(Provider.MICROSOFT_365) == ["Calendars.Read", "Calendars.ReadWrite"]


def test_default_scopes_empty_env():
    """Test that empty ENV returns fallback defaults."""
    with patch.dict(os.environ, {"INTEGRATIONS_DEFAULT_SCOPES_GOOGLE": ""}):
        scopes = get_default_scopes(Provider.GOOGLE)
        assert scopes == ["calendar.readonly"]

