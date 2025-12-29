# AI Shield - System-Dokumentation

## 📋 Inhaltsverzeichnis

1. [System-Übersicht](#system-übersicht)
2. [Architektur](#architektur)
3. [Komponenten](#komponenten)
4. [Installation & Setup](#installation--setup)
5. [Konfiguration](#konfiguration)
6. [Services & Ports](#services--ports)
7. [API-Referenz](#api-referenz)
8. [Monitoring & Observability](#monitoring--observability)
9. [Sicherheit](#sicherheit)
10. [Troubleshooting](#troubleshooting)

---

## System-Übersicht

AI Shield ist ein umfassendes Sicherheits-Gateway für LLM-Anwendungen, das folgende Funktionen bietet:

- ✅ **Prompt-Injection-Schutz** - Blockiert verdächtige Eingaben
- ✅ **PII-Masking** - Maskiert E-Mails, Telefonnummern und Kreditkartendaten
- ✅ **MCP-Tool-Policy-Enforcement** - Kontrolliert Tool-Zugriff basierend auf Presets
- ✅ **MCP-Server-Registry** - Zentrale Verwaltung von MCP-Servern
- ✅ **Observability** - Langfuse, OpenTelemetry, Grafana
- ✅ **Caching** - Redis für Performance
- ✅ **Rate Limiting** - Nginx-basierter Schutz

---

## Architektur

### Routing-Übersicht

AI Shield kann auf zwei Arten integriert werden:

1. **Frontend → Control Plane**: Frontend-Applikationen können direkt mit dem Control Plane kommunizieren über `/api/shield/*` Proxy-Routen
2. **Backend → Gateway**: Node/Python-Backends routen LLM-Requests über das Gateway (Port 4050)

```
Frontend (Next.js)
    │
    ├──► /api/shield/* → Control Plane (Port 4051)
    │                     - MCP Registry
    │                     - Tool Management
    │
    └──► /api/settings/ai-shield → Node Backend → DB

Node Backend / Python Backend
    │
    └──► AI_SHIELD_ENABLED=true
             │
             └──► Gateway (Port 4050)
                      │
                      ├──► Policy Engine (policy_engine.py)
                      ├──► Custom Callbacks
                      └──► OpenAI / LLM Provider (upstream)
```

### Service-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx (Port 80)                       │
│                    Rate Limiting & Routing                   │
└──────────────┬──────────────────────┬────────────────────────┘
               │                      │
               ▼                      ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Gateway         │    │  Control Plane    │
    │  (LiteLLM)       │    │  (FastAPI)       │
    │  Port 4050       │    │  Port 4051       │
    └────────┬─────────┘    └──────────────────┘
             │
             ├──► PostgreSQL (LiteLLM DB)
             ├──► Redis (Caching)
             ├──► Presidio Analyzer/Anonymizer
             ├──► OpenTelemetry Collector
             └──► Langfuse (Observability)
                     │
                     └──► PostgreSQL (Langfuse DB)

┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
├─────────────────────────────────────────────────────────────┤
│  • Jaeger (Tracing) - Port 16686                            │
│  • Prometheus (Metrics) - Port 9090                         │
│  • Grafana (Dashboards) - Port 3001                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Komponenten

### 1. Gateway (LiteLLM)

**Container:** `ai-shield-gateway`  
**Image:** `ghcr.io/berriai/litellm-database:main-v1.80.8-stable`  
**Port:** `4050` (konfigurierbar via `AI_SHIELD_HOST_PORT`)

**Funktionen:**
- LLM-API-Proxy (OpenAI, Anthropic, etc.)
- Custom Callbacks für Sicherheitsprüfungen
- Langfuse-Integration für Tracing
- Redis-Caching
- Database-basierte Konfiguration

**Konfiguration:**
- `apps/gateway/config.yaml` - LiteLLM-Konfiguration
- `apps/gateway/custom_callbacks.py` - AI Shield Callbacks
- `apps/gateway/policies/presets.yaml` - Sicherheits-Presets

---

### 2. Control Plane

**Container:** `ai-shield-control-plane`  
**Image:** Custom Build (`apps/control-plane/Dockerfile`)  
**Port:** `4051` (konfigurierbar via `CONTROL_PLANE_HOST_PORT`)

**Funktionen:**
- MCP-Server-Registry-Verwaltung
- Tool-Pinning und Kategorisierung
- LiteLLM-Konfiguration-Export
- OpenAPI/Swagger-Dokumentation

**API-Dokumentation:**
- Swagger UI: `http://localhost:4051/docs`
- ReDoc: `http://localhost:4051/redoc`
- OpenAPI JSON: `http://localhost:4051/openapi.json`

---

### 3. PostgreSQL

**Container:** `ai-shield-postgres` (LiteLLM)  
**Container:** `ai-shield-postgres-langfuse` (Langfuse)  
**Image:** `postgres:16-alpine`

**Ports:**
- LiteLLM DB: `5435` (konfigurierbar via `POSTGRES_HOST_PORT`)
- Langfuse DB: `5436` (konfigurierbar via `LANGFUSE_DB_PORT`)

**Datenbanken:**
- `litellm` - LiteLLM-Daten (Keys, Teams, Users, MCP, Logs)
- `langfuse` - Langfuse-Daten (Traces, Prompts, Costs)

---

### 4. Redis

**Container:** `ai-shield-redis`  
**Image:** `redis:7-alpine`  
**Port:** `6379` (konfigurierbar via `REDIS_PORT`)

**Funktionen:**
- Response-Caching für LiteLLM
- Performance-Optimierung
- Reduzierung von API-Calls

---

### 5. Presidio

**Container:** `ai-shield-presidio-analyzer`  
**Container:** `ai-shield-presidio-anonymizer`  
**Images:** `mcr.microsoft.com/presidio-analyzer:latest`  
**Images:** `mcr.microsoft.com/presidio-anonymizer:latest`

**Ports:**
- Analyzer: `5001` (konfigurierbar via `PRESIDIO_ANALYZER_HOST_PORT`)
- Anonymizer: `5002` (konfigurierbar via `PRESIDIO_ANONYMIZER_HOST_PORT`)

**Funktionen:**
- PII-Erkennung (E-Mail, Telefon, Kreditkarte, etc.)
- PII-Maskierung

---

### 6. OpenTelemetry Collector

**Container:** `ai-shield-otel-collector`  
**Image:** `otel/opentelemetry-collector-contrib:0.103.0`  
**Ports:**
- gRPC: `4317` (konfigurierbar via `OTEL_GRPC_PORT`)
- HTTP: `4318` (konfigurierbar via `OTEL_HTTP_PORT`)

**Funktionen:**
- Sammlung von Traces, Metrics, Logs
- Export zu Jaeger, Prometheus
- Konfiguration: `deploy/otel-collector.yaml`

---

### 7. Langfuse

**Container:** `ai-shield-langfuse`  
**Image:** `langfuse/langfuse:latest`  
**Port:** `3000` (konfigurierbar via `LANGFUSE_PORT`)

**Funktionen:**
- LLM-Request-Tracing
- Prompt-Management
- Kosten-Tracking
- Debugging

**Zugriff:**
- Web UI: `http://localhost:3000`
- API: `http://localhost:3000/api`

---

### 8. Monitoring Stack

#### Jaeger
**Container:** `ai-shield-jaeger`  
**Image:** `jaegertracing/all-in-one:latest`  
**Port:** `16686` (konfigurierbar via `JAEGER_UI_PORT`)

**Zugriff:** `http://localhost:16686`

#### Prometheus
**Container:** `ai-shield-prometheus`  
**Image:** `prom/prometheus:latest`  
**Port:** `9090` (konfigurierbar via `PROMETHEUS_PORT`)

**Zugriff:** `http://localhost:9090`

#### Grafana
**Container:** `ai-shield-grafana`  
**Image:** `grafana/grafana:latest`  
**Port:** `3001` (konfigurierbar via `GRAFANA_PORT`)

**Zugriff:** `http://localhost:3001`  
**Default Credentials:**
- User: `admin` (konfigurierbar via `GRAFANA_ADMIN_USER`)
- Password: `admin` (konfigurierbar via `GRAFANA_ADMIN_PASSWORD`)

---

### 9. Nginx

**Container:** `ai-shield-nginx`  
**Image:** `nginx:alpine`  
**Port:** `80` (konfigurierbar via `NGINX_PORT`)

**Funktionen:**
- Rate Limiting (10 req/s für Gateway, 5 req/s für Control Plane)
- Reverse Proxy
- Load Balancing (vorbereitet)
- SSL/TLS-Terminierung (konfigurierbar)

**Routing:**
- `/` → Gateway (Port 4050)
- `control-plane.local` → Control Plane (Port 4051)
- `langfuse.local` → Langfuse (Port 3000)

---

## Installation & Setup

### Voraussetzungen

- Docker & Docker Compose
- Mindestens 4GB RAM
- Mindestens 10GB freier Speicherplatz

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/madetocreate/ai-shield.git
cd ai-shield

# .env Datei erstellen
cp .env.example .env  # Falls vorhanden, sonst manuell erstellen

# Umgebungsvariablen setzen (siehe Konfiguration)
nano .env

# Services starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f gateway
```

### Erste Schritte

1. **Gateway testen:**
   ```bash
   curl http://localhost:4050/health
   ```

2. **Control Plane testen:**
   ```bash
   curl http://localhost:4051/health
   ```

3. **Langfuse öffnen:**
   ```bash
   open http://localhost:3000
   ```

4. **Grafana öffnen:**
   ```bash
   open http://localhost:3001
   ```

---

## Konfiguration

### Umgebungsvariablen (.env)

#### Gateway
```env
# OpenAI API Key
OPENAI_API_KEY=sk-...

# LiteLLM Master Key (für API-Authentifizierung)
LITELLM_MASTER_KEY=your-master-key

# Database
DATABASE_URL=postgresql://litellm:${POSTGRES_PASSWORD}@postgres:5432/litellm

# Langfuse Integration
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=http://langfuse:3000

# Policy-Konfiguration
AI_SHIELD_POLICY_PATH=/app/policies/presets.yaml
AI_SHIELD_PRESET_DEFAULT=public_website
AI_SHIELD_REGISTRY_PATH=/app/control-plane-data/mcp_registry.json

# Optional: LLM Guard
AI_SHIELD_ENABLE_TOXICITY_CHECK=false
AI_SHIELD_ENABLE_OUTPUT_SCAN=false
```

#### Control Plane
```env
# Admin-Authentifizierung
CONTROL_PLANE_ADMIN_KEY=your-admin-key-min-32-chars

# Gateway-Integration
GATEWAY_BASE_URL=http://gateway:4000
GATEWAY_ADMIN_KEY=${LITELLM_MASTER_KEY}

# Registry-Pfad
CONTROL_PLANE_REGISTRY_PATH=/app/data/mcp_registry.json
```

#### Langfuse
```env
# Database
LANGFUSE_DB_PASSWORD=langfuse-password

# Secrets
LANGFUSE_SECRET=your-nextauth-secret-min-32-chars
```

#### PostgreSQL
```env
POSTGRES_PASSWORD=your-postgres-password
```

#### Ports (optional, Defaults in Klammern)
```env
AI_SHIELD_HOST_PORT=4050
CONTROL_PLANE_HOST_PORT=4051
LANGFUSE_PORT=3000
GRAFANA_PORT=3001
PROMETHEUS_PORT=9090
JAEGER_UI_PORT=16686
REDIS_PORT=6379
```

---

### Policy Presets

**Datei:** `apps/gateway/policies/presets.yaml`

**Verfügbare Presets:**
- `public_website` - Strengste Sicherheit (Standard)
- `internal_support` - Moderate Sicherheit
- `ops_agent` - Erlaubt mehr Operationen

**PII-Modi:**
- `mask` - Maskiert sensible Daten
- `block` - Blockiert Requests mit sensiblen Daten

**Preset-Auswahl:**
- Via Request-Metadata: `metadata.ai_shield_preset` oder `metadata.preset`
- Fallback: `default_preset` aus YAML

---

## Services & Ports

| Service | Container | Port | Beschreibung |
|---------|-----------|------|--------------|
| Gateway | `ai-shield-gateway` | 4050 | LiteLLM API Gateway |
| Control Plane | `ai-shield-control-plane` | 4051 | MCP Registry API |
| Langfuse | `ai-shield-langfuse` | 3000 | Observability UI |
| Grafana | `ai-shield-grafana` | 3001 | Monitoring Dashboards |
| Prometheus | `ai-shield-prometheus` | 9090 | Metrics |
| Jaeger | `ai-shield-jaeger` | 16686 | Tracing UI |
| Nginx | `ai-shield-nginx` | 80 | Reverse Proxy |
| PostgreSQL (LiteLLM) | `ai-shield-postgres` | 5435 | LiteLLM Database |
| PostgreSQL (Langfuse) | `ai-shield-postgres-langfuse` | 5436 | Langfuse Database |
| Redis | `ai-shield-redis` | 6379 | Cache |
| Presidio Analyzer | `ai-shield-presidio-analyzer` | 5001 | PII Detection |
| Presidio Anonymizer | `ai-shield-presidio-anonymizer` | 5002 | PII Masking |
| OpenTelemetry | `ai-shield-otel-collector` | 4317/4318 | Telemetry |

---

## API-Referenz

### Gateway API (LiteLLM)

**Base URL:** `http://localhost:4050`

#### Chat Completions
```http
POST /v1/chat/completions
Authorization: Bearer <LITELLM_MASTER_KEY>
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "metadata": {
    "ai_shield_preset": "public_website"
  }
}
```

**Sicherheitsprüfungen:**
- Prompt-Injection-Erkennung (Pre-Call)
- PII-Masking (Pre-Call)
- MCP-Tool-Filterung (Pre-Call)

---

### Control Plane API

**Base URL:** `http://localhost:4051`  
**Dokumentation:** `http://localhost:4051/docs`

#### Health Check
```http
GET /health
```

#### Registry abrufen
```http
GET /v1/mcp/registry
x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
```

#### MCP-Server registrieren
```http
POST /v1/mcp/registry
x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
Content-Type: application/json

{
  "server_id": "my-mcp-server",
  "url": "http://localhost:9000/mcp",
  "transport": "streamable_http",
  "auth_type": "none",
  "headers": {},
  "preset": "read_only"
}
```

#### Tools pinnen
```http
POST /v1/mcp/pin/{server_id}
x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
```

#### LiteLLM-Konfiguration exportieren
```http
GET /v1/mcp/litellm-snippet
x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
```

---

## Monitoring & Observability

### Langfuse

**Zugriff:** `http://localhost:3000`

**Features:**
- Request-Tracing
- Prompt-Versionierung
- Kosten-Analyse
- Debugging

**Erste Schritte:**
1. Öffne Langfuse UI
2. Erstelle ein Projekt
3. Kopiere Public/Secret Keys in `.env`
4. Restart Gateway

---

### Grafana

**Zugriff:** `http://localhost:3001`  
**Default Login:** `admin` / `admin`

**Dashboards:**
- AI Shield Overview (automatisch geladen)
- Request Rate
- Error Rate
- Injection Blocks
- PII Detections

**Data Sources:**
- Prometheus (automatisch konfiguriert)

---

### Jaeger

**Zugriff:** `http://localhost:16686`

**Features:**
- Distributed Tracing
- Request-Flows
- Performance-Analyse

---

### Prometheus

**Zugriff:** `http://localhost:9090`

**Metrics:**
- LiteLLM Request Rate
- Error Rate
- AI Shield Blocks
- PII Detections

---

## Sicherheit

### Rate Limiting

**Nginx-basiert:**
- Gateway: 10 req/s (Burst: 20)
- Control Plane: 5 req/s (Burst: 10)

**Konfiguration:** `deploy/nginx.conf`

---

### Authentifizierung

**Gateway:**
- API Key: `Authorization: Bearer <LITELLM_MASTER_KEY>`

**Control Plane:**
- Admin Key: `x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>`

**Empfehlungen:**
- Starke Keys (mindestens 32 Zeichen)
- Keys nicht in Code committed
- Regelmäßige Rotation

---

### PII-Schutz

**Erkannte Typen:**
- E-Mail-Adressen
- Telefonnummern
- Kreditkartennummern (Luhn-validiert)

**Modi:**
- `mask` - Ersetzt durch Platzhalter
- `block` - Blockiert Request

---

### Prompt-Injection-Schutz

**Erkannte Signale:**
- "ignore previous instructions"
- "reveal system prompt"
- "jailbreak"
- Code-Blöcke (```)
- etc.

**Scoring:**
- Jedes Signal: +2 Punkte
- Code-Blöcke: +1 Punkt
- Threshold: 6 (konfigurierbar)

---

## Troubleshooting

### Gateway startet nicht

```bash
# Logs prüfen
docker-compose logs gateway

# Häufige Probleme:
# - DATABASE_URL falsch
# - LITELLM_MASTER_KEY nicht gesetzt
# - PostgreSQL nicht erreichbar
```

### Langfuse zeigt keine Daten

```bash
# Prüfe Keys in .env
# Prüfe Langfuse Health
curl http://localhost:3000/api/public/health

# Prüfe Gateway-Logs
docker-compose logs gateway | grep langfuse
```

### Control Plane antwortet nicht

```bash
# Prüfe Logs
docker-compose logs control-plane

# Prüfe Health
curl http://localhost:4051/health

# Prüfe Admin Key
curl -H "x-ai-shield-admin-key: YOUR_KEY" http://localhost:4051/v1/mcp/registry
```

### Redis-Verbindungsfehler

```bash
# Prüfe Redis Health
docker-compose exec redis redis-cli ping

# Prüfe Gateway-Logs
docker-compose logs gateway | grep redis
```

### Nginx Rate Limiting zu streng

**Anpassen:** `deploy/nginx.conf`
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
# Ändere rate=10r/s zu höherem Wert
```

---

## Routing-Integration

### Frontend → Control Plane

Frontend-Applikationen können über Proxy-Routen mit dem Control Plane kommunizieren:

**Beispiel:** Next.js API Route
```typescript
// frontend/src/app/api/shield/[...path]/route.ts
// Proxied zu: http://localhost:4051/{path}
```

**Verfügbare Endpoints:**
- `GET /api/shield/health` - Health Check
- `GET /api/shield/v1/mcp/registry` - MCP Server Registry
- `POST /api/shield/v1/integrations/{name}/connect` - Integration Connect

### Backend → Gateway (Node/Python)

Backend-Services können LLM-Requests über das Gateway routen:

#### Node Backend

**Konfiguration** (`backend.env`):
```bash
AI_SHIELD_ENABLED=true
AI_SHIELD_GATEWAY_BASE_URL=http://localhost:4050/v1
AI_SHIELD_GATEWAY_KEY=sk-your-master-key
```

**OpenAI Client Routing:**
- Wenn `AI_SHIELD_ENABLED=true`: Routet automatisch über Gateway
- `baseURL` = `AI_SHIELD_GATEWAY_BASE_URL`
- `apiKey` = `AI_SHIELD_GATEWAY_KEY` (Master Key für Gateway Auth)
- Upstream OpenAI Key bleibt im Gateway (nicht im Backend)

**Code:** `Backend/src/integrations/openai/client.ts`

#### Python Backend

**Konfiguration** (`backend.env`):
```bash
AI_SHIELD_ENABLED=true
AI_SHIELD_GATEWAY_BASE_URL=http://localhost:4050/v1
AI_SHIELD_GATEWAY_KEY=sk-your-master-key
```

**Provider Routing:**
- `OpenAICompatibleProvider` prüft `AI_SHIELD_ENABLED`
- Wenn enabled: Nutzt Gateway Base URL + Gateway Key
- Wenn disabled: Nutzt `OPENAI_COMPATIBLE_BASE_URL` + `OPENAI_API_KEY`

**Code:** `backend-agents/app/llm/providers/openai_compatible_provider.py`

### Settings Persistierung

**Frontend Settings:**
- `GET /api/settings/ai-shield` - Lädt Settings aus Node Backend
- `PUT /api/settings/ai-shield` - Speichert Settings in Node Backend DB

**Node Backend:**
- `GET /settings/ai-shield` - Lädt Tenant-spezifische Settings
- `PUT /settings/ai-shield` - Speichert Settings (tenant_id aus Auth Context)

**Schema:**
```typescript
{
  enabled: boolean
  control_plane_url: string | null
  integrations_enabled: Record<string, boolean>
  preset_selection: string | null
}
```

### Testing

**Health Checks:**
```bash
# AI Shield
cd ai-shield && ./scripts/doctor.sh

# Frontend
cd frontend && ./scripts/shield-doctor.sh

# Node Backend
cd Backend && ./scripts/shield-doctor.sh
```

**Smoke Tests:**
```bash
cd ai-shield && ./scripts/smoke.sh
```

---

## Weitere Ressourcen

- **LiteLLM Docs**: https://docs.litellm.ai/
- **Langfuse Docs**: https://langfuse.com/docs
- **Presidio Docs**: https://microsoft.github.io/presidio/
- **OpenTelemetry**: https://opentelemetry.io/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Grafana Docs**: https://grafana.com/docs/

---

## Support

Bei Problemen:
1. Prüfe Logs: `docker-compose logs <service>`
2. Prüfe Health Endpoints
3. Öffne Issue auf GitHub: https://github.com/madetocreate/ai-shield

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2024

