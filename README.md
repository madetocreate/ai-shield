# AI Shield

Ein umfassendes Sicherheits-Gateway für LLM-Anwendungen mit Prompt-Injection-Schutz, PII-Masking, MCP-Tool-Policy-Enforcement und Observability.

## 🚀 Schnellstart

```bash
# Repository klonen
git clone https://github.com/madetocreate/ai-shield.git
cd ai-shield

# 1. Erstelle backend.env mit required docker-compose Variablen
# Standard-Pfad: ~/Documents/Backend-Secrets/backend.env
# Oder setze BACKEND_ENV_PATH Umgebungsvariable
mkdir -p ~/Documents/Backend-Secrets

# 2. Kopiere .env.example als Vorlage (enthält required vars für docker-compose)
cp .env.example ~/Documents/Backend-Secrets/backend.env

# 3. Bearbeite backend.env und setze:
#    - POSTGRES_PASSWORD (required)
#    - LANGFUSE_DB_PASSWORD (required)
#    - LANGFUSE_SECRET (required)
#    - LANGFUSE_URL (required)
#    - GRAFANA_ADMIN_USER (required)
#    - GRAFANA_ADMIN_PASSWORD (required)
#    - OPENAI_API_KEY (für Gateway)
#    - LITELLM_MASTER_KEY (für Gateway)
#    - CONTROL_PLANE_ADMIN_KEY (für Control Plane)

# 4. Services starten (empfohlen: dev-up.sh Script)
./scripts/dev-up.sh

# Alternative: Manuell mit docker-compose
# BACKEND_ENV_PATH=~/Documents/Backend-Secrets/backend.env docker compose --env-file ~/Documents/Backend-Secrets/backend.env up -d

# Logs anzeigen
docker compose logs -f gateway

# Services stoppen
./scripts/dev-down.sh

# Smoke Tests ausführen
./scripts/smoke.sh
```

### 📝 Externe Environment-Konfiguration

AI Shield verwendet **keine .env Datei im Repo**. Stattdessen werden alle Environment-Variablen aus einer externen `backend.env` Datei geladen.

**Standard-Pfad:** `~/Documents/Backend-Secrets/backend.env`

**Alternativ:** Setze die Umgebungsvariable `BACKEND_ENV_PATH` vor dem Start:
```bash
export BACKEND_ENV_PATH=/path/to/your/backend.env
docker-compose up -d
```

**Warum extern?**
- ✅ Keine Secrets im Repository
- ✅ Zentrale Verwaltung aller Backend-Services
- ✅ Einfaches Teilen zwischen Entwicklern (ohne Repo-Zugriff)
- ✅ Production-ready (Docker Secrets / K8s ConfigMaps)

**Wichtig:** `.env.example` enthält die **required Variablen für docker-compose** (POSTGRES_PASSWORD, etc.).
Diese müssen in `backend.env` gesetzt werden, damit `docker-compose up` erfolgreich startet.
Siehe `.env.example` für alle verfügbaren Variablen und Port-Konfigurationen.

## ✨ Features

- ✅ **Prompt-Injection-Schutz** - Blockiert verdächtige Eingaben
- ✅ **PII-Masking** - Maskiert E-Mails, Telefonnummern und Kreditkartendaten
- ✅ **MCP-Tool-Policy-Enforcement** - Kontrolliert Tool-Zugriff basierend auf Presets
- ✅ **MCP-Server-Registry** - Zentrale Verwaltung von MCP-Servern
- ✅ **Observability** - Langfuse, OpenTelemetry, Grafana, Jaeger
- ✅ **Caching** - Redis für Performance
- ✅ **Rate Limiting** - Nginx-basierter Schutz

## 📚 Dokumentation

- **[System-Dokumentation](docs/SYSTEM_DOCUMENTATION.md)** - Vollständige System-Dokumentation
- **[Benutzerhandbuch](docs/README.md)** - Feature-Dokumentation und API-Referenz
- **[Sicherheit & Installation](docs/security.md)** - Erweiterungen und Verbesserungen

## 🏗️ Architektur

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         AI Shield Gateway           │
│  (LiteLLM + Custom Callbacks)       │
│                                     │
│  • Prompt Injection Detection       │
│  • PII Masking                      │
│  • MCP Tool Filtering               │
│  • Policy Enforcement              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      LLM Provider (OpenAI, etc.)    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Control Plane API              │
│                                     │
│  • MCP Server Registry              │
│  • Tool Pinning & Categorization   │
│  • Policy Management               │
└─────────────────────────────────────┘
```

## 🔧 Services

| Service | Port | Beschreibung |
|---------|------|--------------|
| Gateway | 4050 | LiteLLM API Gateway |
| Control Plane | 4051 | MCP Registry API |
| Langfuse | 3000 | Observability UI |
| Grafana | 3001 | Monitoring Dashboards |
| Prometheus | 9090 | Metrics |
| Jaeger | 16686 | Tracing UI |
| Nginx | 80 | Reverse Proxy |

## 📦 Komponenten

- **Gateway** - LiteLLM-basiertes Proxy-Gateway mit Sicherheits-Callbacks
- **Control Plane** - FastAPI-basierte MCP-Server-Verwaltung
- **PostgreSQL** - Datenbank für LiteLLM und Langfuse
- **Redis** - Caching für Performance
- **Presidio** - PII-Erkennung und -Maskierung
- **OpenTelemetry** - Telemetrie-Sammlung
- **Langfuse** - LLM-Request-Tracing
- **Grafana** - Monitoring-Dashboards
- **Jaeger** - Distributed Tracing
- **Prometheus** - Metrics Collection
- **Nginx** - Rate Limiting und Reverse Proxy

## 🐳 Docker Compose Overrides

AI Shield verwendet mehrere Docker Compose Override-Dateien für verschiedene Konfigurationen:

### Empfohlene Kombinationen

**Development (Standard):**
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

**Production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.override.prod-hardening.yml up -d
```

**Mit Langfuse v3 (ClickHouse + MinIO):**
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml \
  -f docker-compose.override.langfuse-v3.yml \
  -f docker-compose.override.langfuse-clickhouse.yml \
  -f docker-compose.override.langfuse-minio.yml up -d
```

### Override-Dateien Übersicht

- `docker-compose.override.yml` - Standard Dev-Overrides (Ports, Volumes)
- `docker-compose.prod.yml` - Production-Konfiguration
- `docker-compose.override.prod-hardening.yml` - Production Security Hardening
- `docker-compose.override.langfuse-v3.yml` - Langfuse v3 Setup
- `docker-compose.override.langfuse-clickhouse.yml` - ClickHouse für Langfuse
- `docker-compose.override.langfuse-minio.yml` - MinIO für Langfuse S3
- `docker-compose.override.tls.yml` - TLS/HTTPS Konfiguration
- `docker-compose.override.minio-fix.yml` - MinIO Healthcheck Fix
- `docker-compose.override.local-ports.yml` - Alternative Port-Mappings
- `docker-compose.override.ai-shield.yml` - AI Shield spezifische Overrides

**Hinweis:** Die meisten anderen Override-Dateien sind experimentell oder für spezifische Fixes. Verwenden Sie die empfohlenen Kombinationen oben.

## 🚦 Erste Schritte

1. **Services starten:**
   ```bash
   ./scripts/dev-up.sh
   ```

2. **Health Checks:**
   ```bash
   curl http://localhost:4050/health  # Gateway
   curl http://localhost:4051/health  # Control Plane
   ```

3. **Smoke Tests:**
   ```bash
   ./scripts/smoke.sh
   ```

4. **Langfuse öffnen:**
   ```bash
   open http://localhost:3000
   ```

5. **Grafana öffnen:**
   ```bash
   open http://localhost:3001
   ```

## 🔐 Nginx htpasswd (Optional)

Falls Nginx Basic Auth benötigt wird:

```bash
# Erstelle htpasswd Datei
docker run --rm httpd:2.4-alpine htpasswd -nbB admin 'CHANGE_ME' > deploy/nginx.htpasswd
```

Die Datei wird automatisch in den Nginx-Container gemountet. Falls sie nicht existiert, startet Nginx trotzdem (Auth wird übersprungen).

## 🔐 Konfiguration

Siehe [.env.example](.env.example) für alle verfügbaren Umgebungsvariablen.

**Wichtigste Variablen:**
- `OPENAI_API_KEY` - OpenAI API Key
- `LITELLM_MASTER_KEY` - Master Key für Gateway-Authentifizierung
- `CONTROL_PLANE_ADMIN_KEY` - Admin Key für Control Plane
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` - Langfuse Keys

**Konfigurationsdatei:** Alle Variablen werden aus `backend.env` geladen (Standard: `~/Documents/Backend-Secrets/backend.env`).

## 📖 Weitere Informationen

- **LiteLLM**: https://docs.litellm.ai/
- **Langfuse**: https://langfuse.com/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Presidio**: https://microsoft.github.io/presidio/

## 🤝 Beitragen

Beiträge sind willkommen! Bitte öffne ein Issue oder erstelle einen Pull Request.

## 📄 Lizenz

MIT

---

**Version:** 1.0.0

