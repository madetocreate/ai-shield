#!/usr/bin/env python3
"""
Nango Provider Setup Script
Configures all hotel and real estate providers in Nango via API
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional

# Configuration
NANGO_BASE_URL = os.environ.get("NANGO_BASE_URL", "http://127.0.0.1:3003")
NANGO_API_KEY = os.environ.get("NANGO_API_KEY", "")

# Provider configurations
HOTEL_PROVIDERS = [
    {
        "provider_key": "booking-com",
        "auth_url": "https://account.booking.com/oauth2/authorize",
        "token_url": "https://account.booking.com/oauth2/token",
        "scopes": "read write",
        "name": "Booking.com"
    },
    {
        "provider_key": "airbnb",
        "auth_url": "https://www.airbnb.com/oauth2/authorize",
        "token_url": "https://www.airbnb.com/oauth2/token",
        "scopes": "read write",
        "name": "Airbnb"
    },
    {
        "provider_key": "expedia",
        "auth_url": "https://api.expediapartnercentral.com/oauth2/authorize",
        "token_url": "https://api.expediapartnercentral.com/oauth2/token",
        "scopes": "read write",
        "name": "Expedia"
    },
    {
        "provider_key": "hrs",
        "auth_url": "https://api.hrs.com/oauth2/authorize",
        "token_url": "https://api.hrs.com/oauth2/token",
        "scopes": "read write",
        "name": "HRS"
    },
    {
        "provider_key": "hotels-com",
        "auth_url": "https://api.hotels.com/oauth2/authorize",
        "token_url": "https://api.hotels.com/oauth2/token",
        "scopes": "read write",
        "name": "Hotels.com"
    },
    {
        "provider_key": "trivago",
        "auth_url": "https://api.trivago.com/oauth2/authorize",
        "token_url": "https://api.trivago.com/oauth2/token",
        "scopes": "read write",
        "name": "Trivago"
    },
    {
        "provider_key": "agoda",
        "auth_url": "https://api.agoda.com/oauth2/authorize",
        "token_url": "https://api.agoda.com/oauth2/token",
        "scopes": "read write",
        "name": "Agoda"
    },
    {
        "provider_key": "padel",
        "auth_url": "https://api.padel.com/oauth2/authorize",
        "token_url": "https://api.padel.com/oauth2/token",
        "scopes": "read write",
        "name": "Padel"
    },
]

HEALTH_PROVIDERS = [
    {
        "provider_key": "microsoft-365",
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scopes": "Calendars.Read Calendars.ReadWrite Mail.Read",
        "name": "Microsoft 365"
    },
    {
        "provider_key": "zoom",
        "auth_url": "https://zoom.us/oauth/authorize",
        "token_url": "https://zoom.us/oauth/token",
        "scopes": "meeting:read meeting:write",
        "name": "Zoom"
    },
    {
        "provider_key": "calendly",
        "auth_url": "https://auth.calendly.com/oauth/authorize",
        "token_url": "https://auth.calendly.com/oauth/token",
        "scopes": "read",
        "name": "Calendly"
    },
    {
        "provider_key": "doxy-me",
        "auth_url": "https://doxy.me/oauth/authorize",
        "token_url": "https://doxy.me/oauth/token",
        "scopes": "read write",
        "name": "Doxy.me"
    },
    {
        "provider_key": "simplepractice",
        "auth_url": "https://api.simplepractice.com/oauth/authorize",
        "token_url": "https://api.simplepractice.com/oauth/token",
        "scopes": "read write",
        "name": "SimplePractice"
    },
    {
        "provider_key": "jane-app",
        "auth_url": "https://api.janeapp.com/oauth/authorize",
        "token_url": "https://api.janeapp.com/oauth/token",
        "scopes": "read write",
        "name": "Jane App"
    },
    {
        "provider_key": "epic-mychart",
        "auth_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize",
        "token_url": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
        "scopes": "patient.read appointment.read appointment.write",
        "name": "Epic MyChart"
    },
    {
        "provider_key": "doctolib",
        "auth_url": "https://www.doctolib.de/oauth/authorize",
        "token_url": "https://www.doctolib.de/oauth/token",
        "scopes": "read write",
        "name": "Doctolib"
    },
]

REAL_ESTATE_PROVIDERS = [
    {
        "provider_key": "immobilienscout24",
        "auth_url": "https://api.immobilienscout24.de/oauth2/authorize",
        "token_url": "https://api.immobilienscout24.de/oauth2/token",
        "scopes": "read write publish",
        "name": "Immobilienscout24"
    },
    {
        "provider_key": "idealista",
        "auth_url": "https://api.idealista.com/oauth/authorize",
        "token_url": "https://api.idealista.com/oauth/token",
        "scopes": "read write publish",
        "name": "Idealista"
    },
    {
        "provider_key": "immowelt",
        "auth_url": "https://api.immowelt.de/oauth2/authorize",
        "token_url": "https://api.immowelt.de/oauth2/token",
        "scopes": "read write",
        "name": "ImmoWelt"
    },
    {
        "provider_key": "ebay-kleinanzeigen",
        "auth_url": "https://api.ebay-kleinanzeigen.de/oauth2/authorize",
        "token_url": "https://api.ebay-kleinanzeigen.de/oauth2/token",
        "scopes": "read write publish",
        "name": "eBay Kleinanzeigen"
    },
    {
        "provider_key": "wohnung-de",
        "auth_url": "https://api.wohnung.de/oauth2/authorize",
        "token_url": "https://api.wohnung.de/oauth2/token",
        "scopes": "read write",
        "name": "Wohnung.de"
    },
    {
        "provider_key": "immonet",
        "auth_url": "https://api.immonet.de/oauth2/authorize",
        "token_url": "https://api.immonet.de/oauth2/token",
        "scopes": "read write",
        "name": "Immonet"
    },
    {
        "provider_key": "fotocasa",
        "auth_url": "https://api.fotocasa.es/oauth2/authorize",
        "token_url": "https://api.fotocasa.es/oauth2/token",
        "scopes": "read write publish",
        "name": "Fotocasa"
    },
    {
        "provider_key": "habitaclia",
        "auth_url": "https://api.habitaclia.com/oauth2/authorize",
        "token_url": "https://api.habitaclia.com/oauth2/token",
        "scopes": "read write publish",
        "name": "Habitaclia"
    },
]


def check_provider_exists(provider_key: str) -> bool:
    """Check if provider already exists."""
    try:
        response = requests.get(
            f"{NANGO_BASE_URL}/config/{provider_key}",
            headers={"Authorization": f"Bearer {NANGO_API_KEY}"},
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False


def create_provider(provider_config: Dict, client_id: str = "", client_secret: str = "") -> bool:
    """Create or update a provider configuration."""
    provider_key = provider_config["provider_key"]
    name = provider_config["name"]
    
    # Check if exists
    if check_provider_exists(provider_key):
        print(f"  ⚠️  {name} ({provider_key}) - Already exists, skipping")
        return True
    
    # Prepare config
    config_data = {
        "provider_config_key": provider_key,
        "provider": "oauth2",
        "authorization_url": provider_config["auth_url"],
        "token_url": provider_config["token_url"],
        "oauth_scopes": provider_config["scopes"],
    }
    
    # Add credentials if provided
    if client_id and client_secret:
        config_data["oauth_client_id"] = client_id
        config_data["oauth_client_secret"] = client_secret
    else:
        config_data["oauth_client_id"] = f"YOUR_{provider_key.upper().replace('-', '_')}_CLIENT_ID"
        config_data["oauth_client_secret"] = f"YOUR_{provider_key.upper().replace('-', '_')}_CLIENT_SECRET"
    
    try:
        response = requests.post(
            f"{NANGO_BASE_URL}/config",
            headers={
                "Authorization": f"Bearer {NANGO_API_KEY}",
                "Content-Type": "application/json"
            },
            json=config_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✅ {name} ({provider_key}) - Created successfully")
            return True
        else:
            print(f"  ❌ {name} ({provider_key}) - Failed: {response.status_code}")
            print(f"     Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ {name} ({provider_key}) - Error: {str(e)}")
        return False


def main():
    """Main function."""
    print("🚀 Nango Provider Setup")
    print(f"📍 Nango URL: {NANGO_BASE_URL}")
    print()
    
    if not NANGO_API_KEY:
        print("❌ NANGO_API_KEY not set!")
        print("   Set it via: export NANGO_API_KEY='your-key'")
        print("   Or get it from Nango Dashboard: http://localhost:3003")
        sys.exit(1)
    
    # Test connection
    try:
        response = requests.get(
            f"{NANGO_BASE_URL}/health",
            timeout=5
        )
        if response.status_code != 200:
            print(f"❌ Nango not reachable (HTTP {response.status_code})")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to Nango: {str(e)}")
        sys.exit(1)
    
    print("📋 Hotel & Booking Platforms:")
    print()
    hotel_success = 0
    for provider in HOTEL_PROVIDERS:
        if create_provider(provider):
            hotel_success += 1
    
    print()
    print("📋 Real Estate Platforms:")
    print()
    realestate_success = 0
    for provider in REAL_ESTATE_PROVIDERS:
        if create_provider(provider):
            realestate_success += 1
    
    print()
    print("📋 Health & Practice Management Platforms:")
    print()
    health_success = 0
    for provider in HEALTH_PROVIDERS:
        if create_provider(provider):
            health_success += 1
    
REVIEW_PROVIDERS = [
    {
        "provider_key": "trustpilot",
        "auth_url": "https://authenticate.trustpilot.com/business-units-api/oauth2/business-users-for-applications/authorize",
        "token_url": "https://authenticate.trustpilot.com/business-units-api/oauth2/business-users-for-applications/accesstoken",
        "scopes": "reviews.read reviews.write invitations.write",
        "name": "Trustpilot"
    },
    {
        "provider_key": "tripadvisor",
        "auth_url": "https://api.tripadvisor.com/oauth2/authorize",
        "token_url": "https://api.tripadvisor.com/oauth2/token",
        "scopes": "reviews.read reviews.write",
        "name": "Tripadvisor"
    },
    {
        "provider_key": "google-reviews",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": "https://www.googleapis.com/auth/business.manage",
        "name": "Google Reviews"
    },
    {
        "provider_key": "yelp",
        "auth_url": "https://api.yelp.com/oauth2/authorize",
        "token_url": "https://api.yelp.com/oauth2/token",
        "scopes": "read write",
        "name": "Yelp"
    },
    {
        "provider_key": "facebook-reviews",
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scopes": "pages_read_engagement pages_manage_posts",
        "name": "Facebook Reviews"
    },
]

    print()
    print("📋 Review Platforms:")
    print()
    review_success = 0
    for provider in REVIEW_PROVIDERS:
        if create_provider(provider):
            review_success += 1
    
    print()
    print("=" * 50)
    print(f"✅ Setup complete!")
    print(f"   Hotel Providers: {hotel_success}/{len(HOTEL_PROVIDERS)}")
    print(f"   Real Estate Providers: {realestate_success}/{len(REAL_ESTATE_PROVIDERS)}")
    print(f"   Health Providers: {health_success}/{len(HEALTH_PROVIDERS)}")
    print(f"   Review Providers: {review_success}/{len(REVIEW_PROVIDERS)}")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Update OAuth credentials in Nango Dashboard")
    print("   - Replace placeholder Client IDs/Secrets with real values")
    print("   - See NANGO_SETUP_GUIDE.md for provider portal links")
    print()


if __name__ == "__main__":
    main()
