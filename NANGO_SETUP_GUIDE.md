# Nango Setup & Konfigurations-Guide

## Übersicht

Dieser Guide erklärt, wie Sie alle Nango Provider für Hotels und Immobilien konfigurieren.

## 1. Nango Dashboard Setup

### 1.1 Nango starten
```bash
cd ~/nango-auth
docker compose up -d
```

### 1.2 Nango Dashboard öffnen
- URL: `http://localhost:3003`
- Standard-Credentials: Siehe `~/nango-auth/.env`

## 2. Provider in Nango konfigurieren

### 2.1 Hotel & Booking Platforms

#### Booking.com
1. **Provider Key**: `booking-com`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://account.booking.com/oauth2/authorize`
4. **Token URL**: `https://account.booking.com/oauth2/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von Booking.com Partner Portal

#### Airbnb
1. **Provider Key**: `airbnb`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://www.airbnb.com/oauth2/authorize`
4. **Token URL**: `https://www.airbnb.com/oauth2/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von Airbnb API Portal

#### Expedia
1. **Provider Key**: `expedia`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.expediapartnercentral.com/oauth2/authorize`
4. **Token URL**: `https://api.expediapartnercentral.com/oauth2/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von Expedia Partner Solutions

#### HRS
1. **Provider Key**: `hrs`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.hrs.com/oauth2/authorize`
4. **Token URL**: `https://api.hrs.com/oauth2/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von HRS Partner Portal

#### Hotels.com
1. **Provider Key**: `hotels-com`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.hotels.com/oauth2/authorize`
4. **Token URL**: `https://api.hotels.com/oauth2/token`
5. **Scopes**: `read`, `write`

#### Trivago
1. **Provider Key**: `trivago`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.trivago.com/oauth2/authorize`
4. **Token URL**: `https://api.trivago.com/oauth2/token`
5. **Scopes**: `read`, `write`

#### Agoda
1. **Provider Key**: `agoda`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.agoda.com/oauth2/authorize`
4. **Token URL**: `https://api.agoda.com/oauth2/token`
5. **Scopes**: `read`, `write`

#### Padel (Spanien)
1. **Provider Key**: `padel`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.padel.com/oauth2/authorize`
4. **Token URL**: `https://api.padel.com/oauth2/token`
5. **Scopes**: `read`, `write`

### 2.2 Real Estate Platforms

#### Immobilienscout24
1. **Provider Key**: `immobilienscout24`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.immobilienscout24.de/oauth2/authorize`
4. **Token URL**: `https://api.immobilienscout24.de/oauth2/token`
5. **Scopes**: `read`, `write`, `publish`
6. **Client ID & Secret**: Von IS24 Partner Portal

#### Idealista (Spanien)
1. **Provider Key**: `idealista`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.idealista.com/oauth/authorize`
4. **Token URL**: `https://api.idealista.com/oauth/token`
5. **Scopes**: `read`, `write`, `publish`
6. **Client ID & Secret**: Von Idealista API Portal

#### ImmoWelt
1. **Provider Key**: `immowelt`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.immowelt.de/oauth2/authorize`
4. **Token URL**: `https://api.immowelt.de/oauth2/token`
5. **Scopes**: `read`, `write`

#### eBay Kleinanzeigen
1. **Provider Key**: `ebay-kleinanzeigen`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.ebay-kleinanzeigen.de/oauth2/authorize`
4. **Token URL**: `https://api.ebay-kleinanzeigen.de/oauth2/token`
5. **Scopes**: `read`, `write`, `publish`

#### Wohnung.de
1. **Provider Key**: `wohnung-de`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.wohnung.de/oauth2/authorize`
4. **Token URL**: `https://api.wohnung.de/oauth2/token`
5. **Scopes**: `read`, `write`

#### Immonet
1. **Provider Key**: `immonet`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.immonet.de/oauth2/authorize`
4. **Token URL**: `https://api.immonet.de/oauth2/token`
5. **Scopes**: `read`, `write`

#### Fotocasa (Spanien)
1. **Provider Key**: `fotocasa`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.fotocasa.es/oauth2/authorize`
4. **Token URL**: `https://api.fotocasa.es/oauth2/token`
5. **Scopes**: `read`, `write`, `publish`

#### Habitaclia (Spanien)
1. **Provider Key**: `habitaclia`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.habitaclia.com/oauth2/authorize`
4. **Token URL**: `https://api.habitaclia.com/oauth2/token`
5. **Scopes**: `read`, `write`, `publish`

## 3. Nango Provider hinzufügen

### Im Nango Dashboard:
1. Gehen Sie zu **"Providers"** → **"Add Provider"**
2. Wählen Sie **"Custom OAuth 2.0"** oder **"Custom OAuth 1.0"**
3. Füllen Sie die Felder aus:
   - **Provider Key**: z.B. `booking-com`
   - **Authorization URL**: Siehe oben
   - **Token URL**: Siehe oben
   - **Client ID**: Von Provider-Portal
   - **Client Secret**: Von Provider-Portal
   - **Scopes**: Siehe oben
4. **Speichern**

## 4. Webhook konfigurieren

### Webhook URL
```
http://localhost:4051/v1/integrations/webhook
```

### Webhook Secret
Siehe `NANGO_WEBHOOK_SECRET` in `.env`

## 5. Testen

### Connection testen:
```bash
curl -X POST http://localhost:3003/connection \
  -H "Authorization: Bearer YOUR_NANGO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_config_key": "booking-com",
    "connection_id": "test-connection",
    "credentials": {
      "access_token": "test-token"
    }
  }'
```

## 6. Troubleshooting

### Häufige Probleme:
1. **"Provider not found"**: Provider Key muss exakt übereinstimmen
2. **"Invalid credentials"**: Client ID/Secret prüfen
3. **"Scope not allowed"**: Scopes in Provider-Portal aktivieren
4. **"Connection timeout"**: Nango Container prüfen (`docker compose ps`)

### 2.3 Health & Practice Management Platforms

#### Microsoft 365
1. **Provider Key**: `microsoft-365`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
4. **Token URL**: `https://login.microsoftonline.com/common/oauth2/v2.0/token`
5. **Scopes**: `Calendars.Read`, `Calendars.ReadWrite`, `Mail.Read`
6. **Client ID & Secret**: Von Azure Portal (App Registration)

#### Zoom
1. **Provider Key**: `zoom`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://zoom.us/oauth/authorize`
4. **Token URL**: `https://zoom.us/oauth/token`
5. **Scopes**: `meeting:read`, `meeting:write`
6. **Client ID & Secret**: Von Zoom Marketplace

#### Calendly
1. **Provider Key**: `calendly`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://auth.calendly.com/oauth/authorize`
4. **Token URL**: `https://auth.calendly.com/oauth/token`
5. **Scopes**: `read`
6. **Client ID & Secret**: Von Calendly Developer Portal

#### Doxy.me
1. **Provider Key**: `doxy-me`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://doxy.me/oauth/authorize`
4. **Token URL**: `https://doxy.me/oauth/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von Doxy.me Partner Portal

#### SimplePractice
1. **Provider Key**: `simplepractice`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.simplepractice.com/oauth/authorize`
4. **Token URL**: `https://api.simplepractice.com/oauth/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von SimplePractice Developer Portal

#### Jane App
1. **Provider Key**: `jane-app`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://api.janeapp.com/oauth/authorize`
4. **Token URL**: `https://api.janeapp.com/oauth/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von Jane App Developer Portal

#### Epic MyChart
1. **Provider Key**: `epic-mychart`
2. **OAuth Type**: OAuth 2.0 (SMART on FHIR)
3. **Authorization URL**: `https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize`
4. **Token URL**: `https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token`
5. **Scopes**: `patient.read`, `appointment.read`, `appointment.write`
6. **Client ID & Secret**: Von Epic App Orchard

#### Doctolib
1. **Provider Key**: `doctolib`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://www.doctolib.de/oauth/authorize`
4. **Token URL**: `https://www.doctolib.de/oauth/token`
5. **Scopes**: `read`, `write`
6. **Client ID & Secret**: Von Doctolib Partner Portal

## 7. API-Dokumentationen

- **Booking.com**: https://developers.booking.com/
- **Airbnb**: https://www.airbnb.com/partner/resources/api
- **Expedia**: https://developer.expediapartnercentral.com/
- **Immobilienscout24**: https://api.immobilienscout24.de/
- **Idealista**: https://developers.idealista.com/
- **Microsoft 365**: https://docs.microsoft.com/en-us/graph/
- **Zoom**: https://marketplace.zoom.us/docs/api-reference/zoom-api
- **Calendly**: https://developer.calendly.com/
- **Epic MyChart**: https://fhir.epic.com/
- **Doctolib**: https://developers.doctolib.com/

### 2.4 Apple Services

#### Apple Sign In
1. **Provider Key**: `apple-signin`
2. **OAuth Type**: OAuth 2.0
3. **Authorization URL**: `https://appleid.apple.com/auth/authorize`
4. **Token URL**: `https://appleid.apple.com/auth/token`
5. **Scopes**: `name`, `email`
6. **Client ID & Secret**: Von Apple Developer Portal
7. **Hinweis**: Erfordert Apple Developer Account ($99/Jahr)

#### iCloud Calendar
1. **Provider Key**: `icloud-calendar`
2. **OAuth Type**: OAuth 2.0 (via iCloud API) oder CalDAV
3. **Authorization URL**: `https://idmsa.apple.com/appleauth/auth/authorize`
4. **Token URL**: `https://idmsa.apple.com/appleauth/auth/token`
5. **Scopes**: `calendars.read`, `calendars.write`
6. **Hinweis**: Eingeschränkt verfügbar, erfordert Enterprise Account oder CalDAV

#### iCloud Drive
1. **Provider Key**: `icloud-drive`
2. **OAuth Type**: OAuth 2.0 (via iCloud API) oder WebDAV
3. **Authorization URL**: `https://idmsa.apple.com/appleauth/auth/authorize`
4. **Token URL**: `https://idmsa.apple.com/appleauth/auth/token`
5. **Scopes**: `drive.read`, `drive.write`
6. **Hinweis**: Eingeschränkt verfügbar, erfordert Enterprise Account oder WebDAV

#### Apple Push Notifications
1. **Provider Key**: `apple-push-notifications`
2. **Auth Type**: JWT-basiert (kein OAuth)
3. **Verwendung**: Push-Benachrichtigungen an iOS/macOS Geräte
4. **Hinweis**: Besser direkt im Backend integriert, nicht über OAuth

**Siehe `APPLE_SERVICES_SETUP.md` für detaillierte Anleitung.**

## 7. API-Dokumentationen

- **Booking.com**: https://developers.booking.com/
- **Airbnb**: https://www.airbnb.com/partner/resources/api
- **Expedia**: https://developer.expediapartnercentral.com/
- **Immobilienscout24**: https://api.immobilienscout24.de/
- **Idealista**: https://developers.idealista.com/
- **Microsoft 365**: https://docs.microsoft.com/en-us/graph/
- **Zoom**: https://marketplace.zoom.us/docs/api-reference/zoom-api
- **Calendly**: https://developer.calendly.com/
- **Epic MyChart**: https://fhir.epic.com/
- **Doctolib**: https://developers.doctolib.com/
- **Apple Sign In**: https://developer.apple.com/sign-in-with-apple/
- **Apple Push Notifications**: https://developer.apple.com/documentation/usernotifications
