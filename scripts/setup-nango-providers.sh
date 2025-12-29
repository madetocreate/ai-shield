#!/bin/bash

# Nango Provider Setup Script
# This script helps configure all hotel and real estate providers in Nango

set -e

NANGO_BASE_URL="${NANGO_BASE_URL:-http://127.0.0.1:3003}"
NANGO_API_KEY="${NANGO_API_KEY:-}"

if [ -z "$NANGO_API_KEY" ]; then
    echo "❌ NANGO_API_KEY not set. Please set it in your environment or .env file"
    echo "   You can find it in the Nango Dashboard: http://localhost:3003"
    exit 1
fi

echo "🚀 Setting up Nango Providers..."
echo "📍 Nango URL: $NANGO_BASE_URL"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to create provider config
create_provider() {
    local provider_key=$1
    local auth_url=$2
    local token_url=$3
    local scopes=$4
    local client_id=$5
    local client_secret=$6
    
    echo -n "  Creating $provider_key... "
    
    # Check if provider already exists
    response=$(curl -s -w "\n%{http_code}" -X GET \
        "$NANGO_BASE_URL/config/$provider_key" \
        -H "Authorization: Bearer $NANGO_API_KEY" \
        -H "Content-Type: application/json" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${YELLOW}Already exists${NC}"
        return 0
    fi
    
    # Create provider
    response=$(curl -s -w "\n%{http_code}" -X POST \
        "$NANGO_BASE_URL/config" \
        -H "Authorization: Bearer $NANGO_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"provider_config_key\": \"$provider_key\",
            \"provider\": \"oauth2\",
            \"oauth_client_id\": \"$client_id\",
            \"oauth_client_secret\": \"$client_secret\",
            \"oauth_scopes\": \"$scopes\",
            \"authorization_url\": \"$auth_url\",
            \"token_url\": \"$token_url\"
        }" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ Created${NC}"
    else
        echo -e "${RED}✗ Failed (HTTP $http_code)${NC}"
        echo "   Response: $(echo "$response" | head -n-1)"
    fi
}

echo "📋 Hotel & Booking Platforms:"
echo ""

# Hotel & Booking Platforms
# Note: Replace CLIENT_ID and CLIENT_SECRET with actual values from provider portals

create_provider "booking-com" \
    "https://account.booking.com/oauth2/authorize" \
    "https://account.booking.com/oauth2/token" \
    "read write" \
    "YOUR_BOOKING_COM_CLIENT_ID" \
    "YOUR_BOOKING_COM_CLIENT_SECRET"

create_provider "airbnb" \
    "https://www.airbnb.com/oauth2/authorize" \
    "https://www.airbnb.com/oauth2/token" \
    "read write" \
    "YOUR_AIRBNB_CLIENT_ID" \
    "YOUR_AIRBNB_CLIENT_SECRET"

create_provider "expedia" \
    "https://api.expediapartnercentral.com/oauth2/authorize" \
    "https://api.expediapartnercentral.com/oauth2/token" \
    "read write" \
    "YOUR_EXPEDIA_CLIENT_ID" \
    "YOUR_EXPEDIA_CLIENT_SECRET"

create_provider "hrs" \
    "https://api.hrs.com/oauth2/authorize" \
    "https://api.hrs.com/oauth2/token" \
    "read write" \
    "YOUR_HRS_CLIENT_ID" \
    "YOUR_HRS_CLIENT_SECRET"

create_provider "hotels-com" \
    "https://api.hotels.com/oauth2/authorize" \
    "https://api.hotels.com/oauth2/token" \
    "read write" \
    "YOUR_HOTELS_COM_CLIENT_ID" \
    "YOUR_HOTELS_COM_CLIENT_SECRET"

create_provider "trivago" \
    "https://api.trivago.com/oauth2/authorize" \
    "https://api.trivago.com/oauth2/token" \
    "read write" \
    "YOUR_TRIVAGO_CLIENT_ID" \
    "YOUR_TRIVAGO_CLIENT_SECRET"

create_provider "agoda" \
    "https://api.agoda.com/oauth2/authorize" \
    "https://api.agoda.com/oauth2/token" \
    "read write" \
    "YOUR_AGODA_CLIENT_ID" \
    "YOUR_AGODA_CLIENT_SECRET"

create_provider "padel" \
    "https://api.padel.com/oauth2/authorize" \
    "https://api.padel.com/oauth2/token" \
    "read write" \
    "YOUR_PADEL_CLIENT_ID" \
    "YOUR_PADEL_CLIENT_SECRET"

echo ""
echo "📋 Real Estate Platforms:"
echo ""

# Real Estate Platforms
create_provider "immobilienscout24" \
    "https://api.immobilienscout24.de/oauth2/authorize" \
    "https://api.immobilienscout24.de/oauth2/token" \
    "read write publish" \
    "YOUR_IS24_CLIENT_ID" \
    "YOUR_IS24_CLIENT_SECRET"

create_provider "idealista" \
    "https://api.idealista.com/oauth/authorize" \
    "https://api.idealista.com/oauth/token" \
    "read write publish" \
    "YOUR_IDEALISTA_CLIENT_ID" \
    "YOUR_IDEALISTA_CLIENT_SECRET"

create_provider "immowelt" \
    "https://api.immowelt.de/oauth2/authorize" \
    "https://api.immowelt.de/oauth2/token" \
    "read write" \
    "YOUR_IMMOWELT_CLIENT_ID" \
    "YOUR_IMMOWELT_CLIENT_SECRET"

create_provider "ebay-kleinanzeigen" \
    "https://api.ebay-kleinanzeigen.de/oauth2/authorize" \
    "https://api.ebay-kleinanzeigen.de/oauth2/token" \
    "read write publish" \
    "YOUR_EBAY_CLIENT_ID" \
    "YOUR_EBAY_CLIENT_SECRET"

create_provider "wohnung-de" \
    "https://api.wohnung.de/oauth2/authorize" \
    "https://api.wohnung.de/oauth2/token" \
    "read write" \
    "YOUR_WOHNUNG_DE_CLIENT_ID" \
    "YOUR_WOHNUNG_DE_CLIENT_SECRET"

create_provider "immonet" \
    "https://api.immonet.de/oauth2/authorize" \
    "https://api.immonet.de/oauth2/token" \
    "read write" \
    "YOUR_IMMONET_CLIENT_ID" \
    "YOUR_IMMONET_CLIENT_SECRET"

create_provider "fotocasa" \
    "https://api.fotocasa.es/oauth2/authorize" \
    "https://api.fotocasa.es/oauth2/token" \
    "read write publish" \
    "YOUR_FOTOCASA_CLIENT_ID" \
    "YOUR_FOTOCASA_CLIENT_SECRET"

create_provider "habitaclia" \
    "https://api.habitaclia.com/oauth2/authorize" \
    "https://api.habitaclia.com/oauth2/token" \
    "read write publish" \
    "YOUR_HABITACLIA_CLIENT_ID" \
    "YOUR_HABITACLIA_CLIENT_SECRET"

echo ""
echo "✅ Provider setup complete!"
echo ""
echo "⚠️  IMPORTANT: Replace all 'YOUR_*_CLIENT_ID' and 'YOUR_*_CLIENT_SECRET' placeholders"
echo "   with actual credentials from the provider portals."
echo ""
echo "📚 See NANGO_SETUP_GUIDE.md for provider portal links and instructions."
