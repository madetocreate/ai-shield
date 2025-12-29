# Fehlende Konfiguration - Nango Integration

## ✅ Bereits konfiguriert

### Nango-Instanz (~/nango-auth/)
- ✅ Docker Compose läuft
- ✅ Postgres, Redis, Nango Server gestartet
- ✅ ENV-Variablen gesetzt (JWT_SECRET, ENCRYPTION_KEY, DB_PASSWORD)

### Backend (.env)
- ✅ `NANGO_BASE_URL=http://127.0.0.1:3003`
- ✅ Default Scopes für alle Provider
- ✅ Safety Settings (WRITE_REQUIRES_APPROVAL, AUDIT_LOG)

## ❌ Noch benötigt

### 1. Nango API Key (für Backend)

**Woher bekommen:**
1. Nango Dashboard öffnen: http://localhost:3009 (Connect UI)
2. Oder API direkt aufrufen: http://localhost:3003
3. In Nango UI: Settings → API Keys → Neuen Key erstellen
4. Oder via API: `POST /api/v1/environment` (wenn Auth aktiviert)

**In Backend .env eintragen:**
```bash
NANGO_API_KEY=<hier-den-api-key-eintragen>
```

### 2. Nango Webhook Secret (optional, für Webhooks)

**Woher bekommen:**
- Wird in Nango UI generiert (Settings → Webhooks)
- Oder selbst generieren: `openssl rand -hex 32`

**In Backend .env eintragen:**
```bash
NANGO_WEBHOOK_SECRET=<hier-den-secret-eintragen>
```

### 3. Provider-Credentials (später, wenn du Provider verbinden willst)

#### Google Calendar
- **Client ID**: Von Google Cloud Console (OAuth 2.0 Client)
- **Client Secret**: Von Google Cloud Console
- **Scopes**: `https://www.googleapis.com/auth/calendar.readonly` (oder mehr)
- **Redirect URI**: `http://localhost:3003/oauth/callback/google`

**Woher bekommen:**
1. Google Cloud Console: https://console.cloud.google.com/
2. Projekt erstellen/auswählen
3. APIs & Services → Credentials
4. OAuth 2.0 Client ID erstellen
5. Authorized redirect URIs: `http://localhost:3003/oauth/callback/google`

#### Shopify
- **Client ID**: Von Shopify App (Custom App)
- **Client Secret**: Von Shopify App
- **Scopes**: `read_orders,read_customers` (oder mehr)
- **Redirect URI**: `http://localhost:3003/oauth/callback/shopify`

**Woher bekommen:**
1. Shopify Partner Dashboard: https://partners.shopify.com/
2. App erstellen (Custom App)
3. Admin API scopes konfigurieren
4. Redirect URL: `http://localhost:3003/oauth/callback/shopify`

#### WooCommerce
- **Consumer Key**: Von WooCommerce → Settings → Advanced → REST API
- **Consumer Secret**: Von WooCommerce → Settings → Advanced → REST API
- **Base URL**: Deine WooCommerce Shop-URL

**Woher bekommen:**
1. WooCommerce Admin → Settings → Advanced → REST API
2. Add Key → Read/Write Permissions
3. Key & Secret kopieren

#### WhatsApp (Meta)
- **App ID**: Von Meta for Developers
- **App Secret**: Von Meta for Developers
- **Phone Number ID**: Von Meta Business Manager
- **Scopes**: `whatsapp_business_messaging`

**Woher bekommen:**
1. Meta for Developers: https://developers.facebook.com/
2. App erstellen (Business → WhatsApp)
3. WhatsApp Business Account verbinden
4. Phone Number ID notieren

## 🔧 Nächste Schritte

### Schritt 1: Nango API Key holen
```bash
# Nango Dashboard öffnen
open http://localhost:3009

# Oder API direkt testen
curl http://localhost:3003/health
```

### Schritt 2: API Key in Backend .env eintragen
```bash
cd /Users/simple-gpt/ai-shield
# .env bearbeiten und NANGO_API_KEY setzen
```

### Schritt 3: Provider konfigurieren (später)
- Provider-Credentials in Nango UI eintragen
- Oder via Nango API konfigurieren

### Schritt 4: Database Migration (später)
- Connections und Approvals von in-memory zu DB migrieren
- SQL-Schema erstellen

## 📝 Aktueller Status

- ✅ Nango läuft: http://localhost:3003
- ✅ Nango UI: http://localhost:3009
- ⏳ API Key: Noch nicht geholt
- ⏳ Provider: Noch nicht konfiguriert
- ⏳ Database: Noch in-memory
