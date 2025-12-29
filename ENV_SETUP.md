# Environment-Konfiguration

## Externe backend.env Datei

AI Shield verwendet **keine .env Datei im Repository**. Stattdessen werden alle Environment-Variablen aus einer externen `backend.env` Datei geladen, die außerhalb des Repos liegt.

### Standard-Pfad

**Standard:** `~/Documents/Backend-Secrets/backend.env`

Dieser Pfad wird automatisch verwendet, wenn keine Umgebungsvariable gesetzt ist.

### Konfigurierbarer Pfad

Du kannst einen anderen Pfad über die Umgebungsvariable `BACKEND_ENV_PATH` setzen:

```bash
export BACKEND_ENV_PATH=/path/to/your/backend.env
docker-compose up -d
```

### Setup

1. **Erstelle das Verzeichnis (falls nicht vorhanden):**
   ```bash
   mkdir -p ~/Documents/Backend-Secrets
   ```

2. **Erstelle backend.env basierend auf .env.example:**
   ```bash
   cp .env.example ~/Documents/Backend-Secrets/backend.env
   ```

3. **Bearbeite backend.env und setze deine Secrets:**
   ```bash
   nano ~/Documents/Backend-Secrets/backend.env
   ```

4. **Starte die Services:**
   ```bash
   docker-compose up -d
   ```

### Warum externe Konfiguration?

- ✅ **Keine Secrets im Repository** - `.env` Dateien werden nie committed
- ✅ **Zentrale Verwaltung** - Eine `backend.env` für alle Backend-Services
- ✅ **Einfaches Teilen** - Entwickler können `backend.env` teilen ohne Repo-Zugriff
- ✅ **Production-ready** - Kompatibel mit Docker Secrets und Kubernetes ConfigMaps
- ✅ **Sicherheit** - Secrets liegen außerhalb des Version-Control-Systems

### Services die backend.env verwenden

- **gateway** - LiteLLM Gateway (OpenAI Keys, Master Key, Database, Langfuse)
- **control-plane** - Control Plane API (Admin Key, Gateway Integration)
- **minio-init** - MinIO Initialisierung (falls MinIO verwendet wird)

### Variablen-Referenz

Siehe [.env.example](.env.example) für eine vollständige Liste aller verfügbaren Environment-Variablen.

### Troubleshooting

**Problem:** Services starten nicht, "env_file not found"

**Lösung:** 
1. Prüfe ob `backend.env` am erwarteten Pfad existiert
2. Setze `BACKEND_ENV_PATH` explizit: `export BACKEND_ENV_PATH=/path/to/backend.env`
3. Prüfe Dateiberechtigungen: `chmod 600 ~/Documents/Backend-Secrets/backend.env`

**Problem:** Variablen werden nicht geladen

**Lösung:**
1. Prüfe ob Variablen in `backend.env` korrekt formatiert sind (keine Leerzeichen um `=`)
2. Prüfe ob Variablen in Docker Compose korrekt referenziert werden: `${VARIABLE_NAME}`
3. Prüfe Logs: `docker-compose logs gateway`

