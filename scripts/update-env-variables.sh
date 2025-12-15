#!/bin/bash

# Update .env file with Nango integration variables
# This script adds/updates the integration environment variables

set -e

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env file not found at: $ENV_FILE"
    echo "   Usage: $0 [path/to/.env]"
    exit 1
fi

echo "📝 Updating $ENV_FILE with Nango integration variables..."
echo ""

# Check if Nango variables already exist
if grep -q "NANGO_BASE_URL" "$ENV_FILE"; then
    echo "⚠️  Nango variables already exist. Updating..."
else
    echo "➕ Adding Nango configuration section..."
    echo "" >> "$ENV_FILE"
    echo "# Nango Integration Configuration" >> "$ENV_FILE"
fi

# Function to add or update variable
add_or_update_var() {
    local var_name=$1
    local default_value=$2
    local comment=$3
    
    if grep -q "^${var_name}=" "$ENV_FILE"; then
        # Update existing
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|^${var_name}=.*|${var_name}=${default_value}|" "$ENV_FILE"
        else
            # Linux
            sed -i "s|^${var_name}=.*|${var_name}=${default_value}|" "$ENV_FILE"
        fi
    else
        # Add new
        if [ -n "$comment" ]; then
            echo "# $comment" >> "$ENV_FILE"
        fi
        echo "${var_name}=${default_value}" >> "$ENV_FILE"
    fi
}

# Nango Configuration
add_or_update_var "NANGO_BASE_URL" "http://127.0.0.1:3003" "Nango Base URL (local or production)"
add_or_update_var "NANGO_API_KEY" "" "Nango API Key (from Nango Dashboard)"
add_or_update_var "NANGO_WEBHOOK_SECRET" "" "Nango Webhook Secret (for webhook verification)"

echo "" >> "$ENV_FILE"
echo "# Integration Safety Settings" >> "$ENV_FILE"
add_or_update_var "INTEGRATIONS_WRITE_REQUIRES_APPROVAL" "1" "Require approval for write operations (1 = enabled, 0 = disabled)"
add_or_update_var "INTEGRATIONS_AUDIT_LOG" "1" "Enable audit logging (1 = enabled, 0 = disabled)"

echo "" >> "$ENV_FILE"
echo "# Integration Default Scopes" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"
echo "# General Integrations" >> "$ENV_FILE"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_GOOGLE" "calendar.readonly"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_GOOGLE_DRIVE" "drive.readonly"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_SHOPIFY" "read_orders,read_customers"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_WOOCOMMERCE" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_HUBSPOT" "contacts.read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_ZENDESK" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_NOTION" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_SLACK" "channels:read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_META" "whatsapp_business_messaging"

echo "" >> "$ENV_FILE"
echo "# Hotel & Booking Platforms" >> "$ENV_FILE"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_BOOKING_COM" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_AIRBNB" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_EXPEDIA" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_HRS" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_HOTELS_COM" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_TRIVAGO" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_AGODA" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_PADEL" "read"

echo "" >> "$ENV_FILE"
echo "# Real Estate Platforms" >> "$ENV_FILE"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_IMMOBILIENSCOUT24" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_IDEALISTA" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_IMMOWELT" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_EBAY_KLEINANZEIGEN" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_WOHNUNG_DE" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_IMMONET" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_FOTOCASA" "read"
add_or_update_var "INTEGRATIONS_DEFAULT_SCOPES_HABITACLIA" "read"

echo ""
echo "✅ Environment variables updated in $ENV_FILE"
echo ""
echo "⚠️  IMPORTANT: Update the following values manually:"
echo "   - NANGO_API_KEY: Get from Nango Dashboard (http://localhost:3003)"
echo "   - NANGO_WEBHOOK_SECRET: Generate a secure random string"
echo ""
