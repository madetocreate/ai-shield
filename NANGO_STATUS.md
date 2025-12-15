# ✅ Nango Integration Status

## 🎉 Erfolgreich gestartet!

### Nango läuft
- ✅ **Health Check**: http://localhost:3003/health → `{"result":"ok"}`
- ✅ **Nango UI**: http://localhost:3009 (Connect UI)
- ✅ **Postgres**: Port 5432
- ✅ **Redis**: Port 6379

### Backend konfiguriert
- ✅ `NANGO_BASE_URL=http://127.0.0.1:3003`
- ✅ Default Scopes für alle Provider
- ✅ Safety Settings aktiviert

## ⚠️ Noch zu tun

### 1. Nango API Key holen (JETZT)

**Option A: Via Nango UI (empfohlen)**
```bash
# Browser öffnen
open http://localhost:3009

# Dann:
# 1. Login/Registrierung (wenn Auth aktiviert)
# 2. Settings → API Keys
# 3. Key kopieren
```

**Option B: Prüfe ob Default Key existiert**
```bash
# Nango ENV prüfen
cd ~/nango-auth
cat .env | grep -i key

# Oder Logs prüfen
docker logs nango-api | grep -i "api\|key" | head -5
```

**Dann in Backend .env eintragen:**
```bash
cd /Users/simple-gpt/ai-shield
# .env bearbeiten:
NANGO_API_KEY=<dein-key-hier>
```

### 2. Provider konfigurieren (SPÄTER)

Wenn du Provider verbinden willst, brauchst du:

- **Google Calendar**: Client ID/Secret von Google Cloud Console
- **Shopify**: App Credentials von Shopify Partner Dashboard
- **WooCommerce**: Consumer Key/Secret von WooCommerce Admin
- **WhatsApp**: App ID/Secret von Meta for Developers

Details siehe: `MISSING_CONFIG.md`

### 3. Database Migration (SPÄTER)

Aktuell: Connections und Approvals in-memory
Später: In Postgres migrieren

## 🧪 Testen

### Backend API testen:
```bash
# Liste aller Connections (sollte leer sein)
curl -H "x-ai-shield-admin-key: $CONTROL_PLANE_ADMIN_KEY" \
     http://localhost:4051/v1/integrations/

# Provider verbinden (Google Beispiel)
curl -X POST \
     -H "Content-Type: application/json" \
     -H "x-ai-shield-admin-key: $CONTROL_PLANE_ADMIN_KEY" \
     -d '{"tenant_id":"test","provider":"google"}' \
     http://localhost:4051/v1/integrations/google/connect
```

### Frontend testen:
- Integrations-Seite öffnen
- Provider-Kacheln sollten sichtbar sein
- "Verbinden" Button sollte funktionieren (nach API Key)

## 📝 Nächste Schritte

1. ✅ Nango gestartet
2. ⏳ API Key holen und in .env eintragen
3. ⏳ Backend neu starten (wenn nötig)
4. ⏳ Frontend testen
5. ⏳ Provider-Credentials konfigurieren (später)
6. ⏳ Database Migration (später)

## 🔗 Wichtige URLs

- **Nango API**: http://localhost:3003
- **Nango UI**: http://localhost:3009
- **Backend API**: http://localhost:4051
- **Health Check**: http://localhost:3003/health

