# AI Shield - Vollständige Dokumentation

## Übersicht

AI Shield ist eine umfassende Plattform für sichere LLM-Nutzung mit Gateway, Control Plane, Observability, und mehr.

## 🏗️ Architektur

### Komponenten

1. **LiteLLM Gateway** (`apps/gateway/`)
   - LLM Request Routing
   - Custom Callbacks
   - Langfuse Integration
   - Redis Caching

2. **Control Plane** (`apps/control-plane/`)
   - FastAPI API
   - Tenant Management
   - Configuration Management

3. **OpenTelemetry Collector** (`deploy/otel-collector.yaml`)
   - Traces, Metrics, Logs
   - Export zu Jaeger, Prometheus, Grafana

4. **Nginx** (`deploy/nginx.conf`)
   - Reverse Proxy
   - Rate Limiting

5. **Monitoring Stack**
   - Prometheus (Metrics)
   - Grafana (Dashboards)
   - Langfuse (LLM Tracing)

## 📋 Features

### ✅ Implementiert

- ✅ LiteLLM Gateway mit Custom Callbacks
- ✅ Langfuse Integration
- ✅ Redis Caching
- ✅ OpenTelemetry Setup
- ✅ Prometheus Metrics
- ✅ Grafana Dashboards
- ✅ Nginx Rate Limiting
- ✅ Control Plane API

## 🔧 Setup & Installation

### Voraussetzungen

- Docker & Docker Compose
- PostgreSQL
- Redis (optional)

### Installation

```bash
# Environment Variables setzen
cp .env.example .env
# Bearbeite .env

# Services starten
docker-compose up -d

# Services stoppen
docker-compose down
```

### Services

- **Gateway**: `http://localhost:4000`
- **Control Plane**: `http://localhost:8000`
- **Langfuse**: `http://localhost:3000`
- **Grafana**: `http://localhost:3001`
- **Prometheus**: `http://localhost:9090`

## 📚 Configuration

### Gateway Config (`apps/gateway/config.yaml`)

```yaml
litellm_settings:
  callbacks:
    - langfuse
  cache:
    type: redis
    host: redis
    port: 6379
```

### Nginx Config (`deploy/nginx.conf`)

- Rate Limiting: 10 requests/second per IP
- Reverse Proxy für alle Services

### Prometheus Config (`deploy/prometheus.yml`)

- Scraping für Nginx, cAdvisor, Node Exporter, etc.

## 🔍 Observability

### OpenTelemetry

- Traces → Jaeger
- Metrics → Prometheus
- Logs → Grafana Loki

### Langfuse

- LLM Request Tracing
- Prompt Management
- Cost Tracking

### Grafana

- Pre-configured Dashboards
- Custom Dashboards möglich

## 🚀 Deployment

### Docker Compose

```bash
# Start
docker-compose up -d

# Logs anzeigen
docker-compose logs -f gateway

# Stop
docker-compose down
```

### Environment Variables

```env
# Gateway
OPENAI_API_KEY=your_key
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_secret

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL
POSTGRES_URL=postgresql://user:pass@postgres:5432/dbname
```

## 📖 Weitere Dokumentation

- [System Documentation](docs/SYSTEM_DOCUMENTATION.md)
- [Installation Suggestions](docs/security.md)
- [Security](docs/security.md)

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature Branch
3. Committe deine Änderungen
4. Push zum Branch
5. Erstelle einen Pull Request

## 📝 License

Proprietary - Alle Rechte vorbehalten

