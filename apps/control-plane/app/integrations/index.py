"""
Integrations Registry

Zentrale Registry für alle Provider-Integrationen.
"""
from typing import Dict, Any
from .types import Provider
from .providers import (
    google, google_drive, shopify, woocommerce, hubspot, zendesk, notion, slack, whatsapp,
    padel,
    apple_signin, icloud_calendar, icloud_drive, apple_push_notifications,
    trustpilot, tripadvisor, google_reviews, yelp, facebook_reviews
)

# Note: Some providers may not be available in Nango by default
# You may need to create custom provider configurations in Nango Dashboard


# Provider registry mapping
PROVIDER_MODULES: Dict[Provider, Any] = {
    # General
    Provider.GOOGLE: google,
    Provider.GOOGLE_DRIVE: google_drive,
    Provider.SHOPIFY: shopify,
    Provider.WOOCOMMERCE: woocommerce,
    Provider.HUBSPOT: hubspot,
    Provider.ZENDESK: zendesk,
    Provider.NOTION: notion,
    Provider.SLACK: slack,
    Provider.WHATSAPP: whatsapp,
    # Booking Platforms
    Provider.PADEL: padel,
    # Apple Services
    Provider.APPLE_SIGNIN: apple_signin,
    Provider.ICLOUD_CALENDAR: icloud_calendar,
    Provider.ICLOUD_DRIVE: icloud_drive,
    Provider.APPLE_PUSH_NOTIFICATIONS: apple_push_notifications,
    # Review Platforms
    Provider.TRUSTPILOT: trustpilot,
    Provider.TRIPADVISOR: tripadvisor,
    Provider.GOOGLE_REVIEWS: google_reviews,
    Provider.YELP: yelp,
    Provider.FACEBOOK_REVIEWS: facebook_reviews,
}

# Note: All providers are registered, but actual API endpoints may vary
# Check NANGO_SETUP_GUIDE.md for provider-specific configuration


def get_provider_module(provider: Provider):
    """Get provider module by provider enum."""
    return PROVIDER_MODULES.get(provider)


__all__ = [
    "Provider",
    "PROVIDER_MODULES",
    "get_provider_module",
]
