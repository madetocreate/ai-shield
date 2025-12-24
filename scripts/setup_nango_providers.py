#!/usr/bin/env python3
"""
Nango Provider Setup Script
Configures core providers in Nango via API
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
BOOKING_PROVIDERS = [
    {
        "provider_key": "padel",
        "auth_url": "https://api.padel.com/oauth2/authorize",
        "token_url": "https://api.padel.com/oauth2/token",
        "scopes": "read write",
        "name": "Padel"
    },
]

CORE_HEALTH_PROVIDERS = [
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
]

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
    
    print("📋 Booking Platforms:")
    print()
    booking_success = 0
    for provider in BOOKING_PROVIDERS:
        if create_provider(provider):
            booking_success += 1
    
    print()
    print("📋 Core Health & Calendar Platforms:")
    print()
    health_success = 0
    for provider in CORE_HEALTH_PROVIDERS:
        if create_provider(provider):
            health_success += 1
    
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
    print(f"   Booking Providers: {booking_success}/{len(BOOKING_PROVIDERS)}")
    print(f"   Core Health Providers: {health_success}/{len(CORE_HEALTH_PROVIDERS)}")
    print(f"   Review Providers: {review_success}/{len(REVIEW_PROVIDERS)}")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Update OAuth credentials in Nango Dashboard")
    print("   - Replace placeholder Client IDs/Secrets with real values")
    print("   - See NANGO_SETUP_GUIDE.md for provider portal links")
    print()


if __name__ == "__main__":
    main()
