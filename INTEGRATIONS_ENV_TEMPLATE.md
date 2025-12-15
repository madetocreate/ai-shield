# Integration Environment Variables Template

## Nango Configuration
```bash
# Nango Base URL (local or production)
NANGO_BASE_URL=http://127.0.0.1:3003

# Nango API Key (from Nango Dashboard)
NANGO_API_KEY=your-nango-api-key-here

# Nango Webhook Secret (for webhook verification)
NANGO_WEBHOOK_SECRET=your-nango-webhook-secret-here
```

## Integration Safety Settings
```bash
# Require approval for write operations (1 = enabled, 0 = disabled)
INTEGRATIONS_WRITE_REQUIRES_APPROVAL=1

# Enable audit logging (1 = enabled, 0 = disabled)
INTEGRATIONS_AUDIT_LOG=1
```

## Integration Default Scopes

### General Integrations
```bash
INTEGRATIONS_DEFAULT_SCOPES_GOOGLE=calendar.readonly
INTEGRATIONS_DEFAULT_SCOPES_GOOGLE_DRIVE=drive.readonly
INTEGRATIONS_DEFAULT_SCOPES_SHOPIFY=read_orders,read_customers
INTEGRATIONS_DEFAULT_SCOPES_WOOCOMMERCE=read
INTEGRATIONS_DEFAULT_SCOPES_HUBSPOT=contacts.read
INTEGRATIONS_DEFAULT_SCOPES_ZENDESK=read
INTEGRATIONS_DEFAULT_SCOPES_NOTION=read
INTEGRATIONS_DEFAULT_SCOPES_SLACK=channels:read
INTEGRATIONS_DEFAULT_SCOPES_META=whatsapp_business_messaging
```

### Hotel & Booking Platforms
```bash
# Booking.com
INTEGRATIONS_DEFAULT_SCOPES_BOOKING_COM=read

# Airbnb
INTEGRATIONS_DEFAULT_SCOPES_AIRBNB=read

# Expedia
INTEGRATIONS_DEFAULT_SCOPES_EXPEDIA=read

# HRS
INTEGRATIONS_DEFAULT_SCOPES_HRS=read

# Hotels.com
INTEGRATIONS_DEFAULT_SCOPES_HOTELS_COM=read

# Trivago
INTEGRATIONS_DEFAULT_SCOPES_TRIVAGO=read

# Agoda
INTEGRATIONS_DEFAULT_SCOPES_AGODA=read

# Padel (Spain)
INTEGRATIONS_DEFAULT_SCOPES_PADEL=read
```

### Real Estate Platforms
```bash
# Immobilienscout24
INTEGRATIONS_DEFAULT_SCOPES_IMMOBILIENSCOUT24=read

# Idealista (Spain)
INTEGRATIONS_DEFAULT_SCOPES_IDEALISTA=read

# ImmoWelt
INTEGRATIONS_DEFAULT_SCOPES_IMMOWELT=read

# eBay Kleinanzeigen
INTEGRATIONS_DEFAULT_SCOPES_EBAY_KLEINANZEIGEN=read

# Wohnung.de
INTEGRATIONS_DEFAULT_SCOPES_WOHNUNG_DE=read

# Immonet
INTEGRATIONS_DEFAULT_SCOPES_IMMONET=read

# Fotocasa (Spain)
INTEGRATIONS_DEFAULT_SCOPES_FOTOCASA=read

# Habitaclia (Spain)
INTEGRATIONS_DEFAULT_SCOPES_HABITACLIA=read
```

### Health & Practice Management Platforms
```bash
# Microsoft 365
INTEGRATIONS_DEFAULT_SCOPES_MICROSOFT_365=Calendars.Read,Calendars.ReadWrite

# Zoom
INTEGRATIONS_DEFAULT_SCOPES_ZOOM=meeting:read,meeting:write

# Calendly
INTEGRATIONS_DEFAULT_SCOPES_CALENDLY=read

# Doxy.me
INTEGRATIONS_DEFAULT_SCOPES_DOXY_ME=read

# SimplePractice
INTEGRATIONS_DEFAULT_SCOPES_SIMPLEPRACTICE=read

# Jane App
INTEGRATIONS_DEFAULT_SCOPES_JANE_APP=read

# Epic MyChart
INTEGRATIONS_DEFAULT_SCOPES_EPIC_MYCHART=patient.read,appointment.read

# Doctolib
INTEGRATIONS_DEFAULT_SCOPES_DOCTOLIB=read
```

### Apple Services
```bash
# Apple Sign In
INTEGRATIONS_DEFAULT_SCOPES_APPLE_SIGNIN=name,email

# iCloud Calendar
INTEGRATIONS_DEFAULT_SCOPES_ICLOUD_CALENDAR=calendars.read,calendars.write

# iCloud Drive
INTEGRATIONS_DEFAULT_SCOPES_ICLOUD_DRIVE=drive.read,drive.write

# Apple Push Notifications
INTEGRATIONS_DEFAULT_SCOPES_APPLE_PUSH_NOTIFICATIONS=notifications.write
```

### Review Platforms
```bash
# Trustpilot
INTEGRATIONS_DEFAULT_SCOPES_TRUSTPILOT=reviews.read,reviews.write,invitations.write

# Tripadvisor
INTEGRATIONS_DEFAULT_SCOPES_TRIPADVISOR=reviews.read,reviews.write

# Google Reviews
INTEGRATIONS_DEFAULT_SCOPES_GOOGLE_REVIEWS=https://www.googleapis.com/auth/business.manage

# Yelp
INTEGRATIONS_DEFAULT_SCOPES_YELP=read

# Facebook Reviews
INTEGRATIONS_DEFAULT_SCOPES_FACEBOOK_REVIEWS=pages_read_engagement,pages_manage_posts
```

## Setup Instructions

1. **Kopieren Sie diese Variablen in Ihre `.env` Datei:**
   ```bash
   cp INTEGRATIONS_ENV_TEMPLATE.md .env
   # Dann manuell die Werte anpassen
   ```

2. **Nango API Key erhalten:**
   - Öffnen Sie Nango Dashboard: `http://localhost:3003`
   - Gehen Sie zu Settings → API Keys
   - Kopieren Sie den API Key

3. **Webhook Secret generieren:**
   - Im Nango Dashboard: Settings → Webhooks
   - Generieren Sie ein Secret oder verwenden Sie ein sicheres Random-String

4. **Provider-spezifische Scopes:**
   - Jeder Provider hat unterschiedliche Scope-Anforderungen
   - Siehe `NANGO_SETUP_GUIDE.md` für Details zu jedem Provider

## Beispiel .env Einträge

```bash
# Nango Configuration
NANGO_BASE_URL=http://127.0.0.1:3003
NANGO_API_KEY=3mtDFIznwTU/qVFWSUYrZT/YoYbI9rbAc1xt51SIu6vJaZ7N
NANGO_WEBHOOK_SECRET=-UjwsZdg9Pd3ErWdKmXAnyBRKCgWYwNvUx3Q41Qqeg8

# Integration Safety
INTEGRATIONS_WRITE_REQUIRES_APPROVAL=1
INTEGRATIONS_AUDIT_LOG=1

# Hotel Platforms
INTEGRATIONS_DEFAULT_SCOPES_BOOKING_COM=read
INTEGRATIONS_DEFAULT_SCOPES_AIRBNB=read
INTEGRATIONS_DEFAULT_SCOPES_EXPEDIA=read
INTEGRATIONS_DEFAULT_SCOPES_HRS=read

# Real Estate Platforms
INTEGRATIONS_DEFAULT_SCOPES_IMMOBILIENSCOUT24=read
INTEGRATIONS_DEFAULT_SCOPES_IDEALISTA=read
INTEGRATIONS_DEFAULT_SCOPES_IMMOWELT=read
```

## Wichtige Hinweise

- **Sicherheit**: Niemals API Keys oder Secrets in Git committen
- **Scopes**: Starten Sie mit `read`-only Scopes für Sicherheit
- **Testing**: Verwenden Sie separate Test-Credentials für Entwicklung
- **Production**: Verwenden Sie starke, eindeutige Secrets für Production
