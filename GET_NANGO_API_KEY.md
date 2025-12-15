# Nango API Key holen

## Option 1: Via Nango UI (empfohlen)

1. **Nango Dashboard öffnen:**
   ```bash
   open http://localhost:3009
   ```

2. **Login/Registrierung:**
   - Wenn Auth aktiviert: Account erstellen
   - Wenn Auth deaktiviert (aktuell): Direkt zugänglich

3. **API Key finden:**
   - Settings → API Keys
   - Oder: Environment → API Keys
   - Neuen Key erstellen oder bestehenden kopieren

## Option 2: Via API (wenn Auth deaktiviert)

Da `FLAG_AUTH_ENABLED=false` ist, sollte der API Key standardmäßig verfügbar sein.

**Test:**
```bash
# Environment Info abrufen
curl http://localhost:3003/api/v1/environment

# Oder direkt testen
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:3003/api/v1/environment
```

## Option 3: Default API Key (Development)

Für Development kann man einen Default-Key setzen. Prüfe Nango Logs:

```bash
docker logs nango-api | grep -i "api\|key\|secret" | head -10
```

## Option 4: Nango ENV prüfen

Manchmal wird der API Key in der .env gesetzt:

```bash
cd ~/nango-auth
cat .env | grep -i "api\|key\|secret"
```

## Was du brauchst

Nachdem du den API Key hast:

1. **In Backend .env eintragen:**
   ```bash
   cd /Users/simple-gpt/ai-shield
   # .env bearbeiten:
   NANGO_API_KEY=<dein-api-key-hier>
   ```

2. **Testen:**
   ```bash
   # Backend neu starten (wenn nötig)
   # Dann testen:
   curl -H "x-ai-shield-admin-key: $CONTROL_PLANE_ADMIN_KEY" \
        http://localhost:4051/v1/integrations/
   ```

## Hinweis

Wenn kein API Key verfügbar ist, kann man auch ohne API Key arbeiten (nur für Development):
- Nango erlaubt manchmal Requests ohne Auth im Development-Modus
- Für Production: Auth aktivieren und API Keys verwenden
