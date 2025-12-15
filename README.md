# AI Shield

Ein umfassendes Sicherheits-Gateway für LLM-Anwendungen mit Prompt-Injection-Schutz, PII-Masking, MCP-Tool-Policy-Enforcement und Observability.

## 🚀 Schnellstart

```bash
# Repository klonen
git clone https://github.com/madetocreate/ai-shield.git
cd ai-shield

# .env Datei erstellen
cp .env.example .env
# Bearbeite .env und setze deine API-Keys

# Services starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f gateway
```

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
- **[Installationsvorschläge](docs/INSTALLATION_SUGGESTIONS.md)** - Erweiterungen und Verbesserungen

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

## 🚦 Erste Schritte

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

## 🔐 Konfiguration

Siehe [.env.example](.env.example) für alle verfügbaren Umgebungsvariablen.

**Wichtigste Variablen:**
- `OPENAI_API_KEY` - OpenAI API Key
- `LITELLM_MASTER_KEY` - Master Key für Gateway-Authentifizierung
- `CONTROL_PLANE_ADMIN_KEY` - Admin Key für Control Plane
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` - Langfuse Keys

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

