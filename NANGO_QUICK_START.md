# Nango Quick Start Guide

## 🚀 Schnellstart

### 1. Nango starten
```bash
cd ~/nango-auth
docker compose up -d
```

### 2. Nango Dashboard öffnen
- URL: `http://localhost:3003`
- Standard-Login: Siehe `~/nango-auth/.env`

### 3. ENV-Variablen aktualisieren
```bash
cd /Users/simple-gpt/ai-shield
./scripts/update-env-variables.sh .env
```

Dann manuell in `.env` eintragen:
- `NANGO_API_KEY`: Aus Nango Dashboard kopieren (Settings → API Keys)
- `NANGO_WEBHOOK_SECRET`: Sicherer Random-String (z.B. `openssl rand -hex 32`)

### 4. Provider konfigurieren

#### Option A: Über Nango Dashboard (Empfohlen)
1. Öffne `http://localhost:3003`
2. Gehe zu **"Providers"** → **"Add Provider"**
3. Wähle **"Custom OAuth 2.0"**
4. Fülle die Felder aus (siehe `NANGO_SETUP_GUIDE.md` für Details)
5. **Speichern**

#### Option B: Über Script (benötigt echte Credentials)
```bash
# Setze NANGO_API_KEY
export NANGO_API_KEY="your-api-key-from-dashboard"

# Führe Setup-Script aus
./scripts/setup-nango-providers.sh
```

**⚠️ WICHTIG**: Ersetze alle `YOUR_*_CLIENT_ID` und `YOUR_*_CLIENT_SECRET` Platzhalter im Script mit echten Credentials von den Provider-Portalen.

### 5. Webhook konfigurieren
Im Nango Dashboard:
1. Gehe zu **Settings** → **Webhooks**
2. Webhook URL: `http://localhost:4051/v1/integrations/webhook`
3. Webhook Secret: Verwende den Wert aus `.env` (`NANGO_WEBHOOK_SECRET`)

### 6. Provider testen
1. Öffne Frontend: `http://localhost:3000/integrations`
2. Klicke auf einen Provider
3. Führe OAuth-Flow durch
4. Prüfe Connection-Status

## 📋 Provider-Liste

### Hotel & Booking (8)
- ✅ Booking.com
- ✅ Airbnb
- ✅ Expedia
- ✅ HRS
- ✅ Hotels.com
- ✅ Trivago
- ✅ Agoda
- ✅ Padel

### Real Estate (8)
- ✅ Immobilienscout24
- ✅ Idealista
- ✅ ImmoWelt
- ✅ eBay Kleinanzeigen
- ✅ Wohnung.de
- ✅ Immonet
- ✅ Fotocasa
- ✅ Habitaclia

## 🔗 Wichtige Links

- **Nango Dashboard**: http://localhost:3003
- **Setup Guide**: `NANGO_SETUP_GUIDE.md`
- **ENV Template**: `INTEGRATIONS_ENV_TEMPLATE.md`
- **Frontend Integrations**: http://localhost:3000/integrations

## ⚠️ Troubleshooting

### Nango Container läuft nicht
```bash
cd ~/nango-auth
docker compose ps
docker compose logs nango-server
```

### API Key nicht gefunden
1. Öffne Nango Dashboard
2. Gehe zu Settings → API Keys
3. Kopiere den API Key
4. Füge ihn in `.env` ein

### Provider nicht gefunden
- Prüfe Provider Key (muss exakt übereinstimmen)
- Prüfe OAuth URLs in `NANGO_SETUP_GUIDE.md`
- Prüfe Client ID/Secret

### Connection Timeout
- Prüfe Nango Container: `docker compose ps`
- Prüfe Logs: `docker compose logs nango-server`
- Prüfe Netzwerk: `curl http://localhost:3003/health`

## 📚 Nächste Schritte

1. ✅ Provider in Nango Dashboard konfigurieren
2. ✅ OAuth Credentials von Provider-Portalen holen
3. ✅ ENV-Variablen setzen
4. ✅ Webhook konfigurieren
5. ✅ Provider testen

Viel Erfolg! 🎉
