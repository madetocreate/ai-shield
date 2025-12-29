# AI Shield - Dokumentation

AI Shield ist ein Sicherheits-Gateway für LLM-Anwendungen, das Prompt-Injection-Schutz, PII-Masking, MCP-Tool-Policy-Enforcement und zentrale MCP-Server-Verwaltung bietet.

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Architektur](#architektur)
3. [Komponenten](#komponenten)
4. [Installation & Setup](#installation--setup)
5. [Konfiguration](#konfiguration)
6. [Features](#features)
7. [API-Referenz](#api-referenz)
8. [Best Practices](#best-practices)

---

## Übersicht

AI Shield besteht aus zwei Hauptkomponenten:

1. **Gateway** - LiteLLM-basiertes Proxy-Gateway mit Sicherheits-Callbacks
2. **Control Plane** - Verwaltung von MCP-Server-Registrierungen und Tool-Policies

### Hauptfunktionen

- ✅ **Prompt-Injection-Erkennung** - Blockiert verdächtige Eingaben
- ✅ **PII-Masking** - Maskiert E-Mails, Telefonnummern und Kreditkartendaten
- ✅ **MCP-Tool-Policy-Enforcement** - Kontrolliert Tool-Zugriff basierend auf Presets
- ✅ **MCP-Server-Registry** - Zentrale Verwaltung von MCP-Servern
- ✅ **Tool-Kategorisierung** - Automatische Klassifizierung von Tools (read/write/dangerous)
- ✅ **Preset-basierte Konfiguration** - Verschiedene Sicherheitsprofile für verschiedene Use-Cases

---

## Architektur

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

---

## Komponenten

### 1. Gateway (`apps/gateway/`)

Das Gateway ist ein LiteLLM-Proxy-Server mit benutzerdefinierten Callbacks für Sicherheitsprüfungen.

**Hauptdateien:**
- `config.yaml` - LiteLLM-Konfiguration
- `custom_callbacks.py` - AI Shield Callback-Implementierung
- `policies/presets.yaml` - Sicherheits-Presets

**Funktionen:**
- Proxy für LLM-API-Calls
- Pre-Call-Hooks für Sicherheitsprüfungen
- Post-Call-Hooks für Logging/Audit
- MCP-Tool-Filterung basierend auf Registry

### 2. Control Plane (`apps/control-plane/`)

Die Control Plane verwaltet MCP-Server-Registrierungen und Tool-Policies.

**Hauptdateien:**
- `app/main.py` - FastAPI-Server für Registry-Verwaltung
- `data/mcp_registry.json` - Persistente Registry-Daten

**Funktionen:**
- MCP-Server-Registrierung
- Tool-Pinning (Erkennung und Kategorisierung)
- Policy-Generierung für LiteLLM
- Registry-Export als YAML

---

## Installation & Setup

### Voraussetzungen

- Docker & Docker Compose
- Mindestens 4GB RAM
- Mindestens 10GB freier Speicherplatz
- Python 3.10+ (für lokale Entwicklung, optional)

### Docker Setup

```bash
# Repository klonen
git clone https://github.com/madetocreate/ai-shield.git
cd ai-shield

# .env Datei erstellen
cp .env.example .env

# Umgebungsvariablen setzen (siehe .env.example)
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

**Detaillierte Dokumentation:** Siehe [SYSTEM_DOCUMENTATION.md](./SYSTEM_DOCUMENTATION.md)

### Lokale Entwicklung

```bash
# Gateway
cd apps/gateway
pip install -r requirements.txt
litellm --config config.yaml --port 4000

# Control Plane
cd apps/control-plane
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8010
```

### Ports

| Service | Port | Beschreibung |
|---------|------|--------------|
| Gateway | `4050` | LiteLLM API Gateway |
| Control Plane | `4051` | MCP Registry API |
| Langfuse | `3000` | Observability UI |
| Grafana | `3001` | Monitoring Dashboards |
| Prometheus | `9090` | Metrics |
| Jaeger | `16686` | Tracing UI |
| Nginx | `80` | Reverse Proxy |
| PostgreSQL (LiteLLM) | `5435` | LiteLLM Database |
| PostgreSQL (Langfuse) | `5436` | Langfuse Database |
| Redis | `6379` | Cache |

Alle Ports sind konfigurierbar via Environment-Variablen (siehe `.env.example`).

---

## Konfiguration

### Umgebungsvariablen

#### Gateway

```env
# OpenAI API Key
OPENAI_API_KEY=sk-...

# LiteLLM Master Key
LITELLM_MASTER_KEY=your-master-key

# Policy-Konfiguration
AI_SHIELD_POLICY_PATH=/app/policies/presets.yaml
AI_SHIELD_PRESET_DEFAULT=public_website
AI_SHIELD_REGISTRY_PATH=/app/control-plane-data/mcp_registry.json
```

#### Control Plane

```env
# Admin-Authentifizierung
CONTROL_PLANE_ADMIN_KEY=your-admin-key

# Gateway-Integration
GATEWAY_BASE_URL=http://gateway:4000
GATEWAY_ADMIN_KEY=${LITELLM_MASTER_KEY}

# Registry-Pfad
CONTROL_PLANE_REGISTRY_PATH=/app/data/mcp_registry.json

# Auto-Quarantine
MCP_AUTO_QUARANTINE=true
MCP_SCAN_INTERVAL_SECONDS=300
```

### Policy Presets (`apps/gateway/policies/presets.yaml`)

```yaml
default_preset: public_website

presets:
  public_website:
    pii:
      email: mask          # E-Mails maskieren
      phone: mask          # Telefonnummern maskieren
      credit_card: block   # Kreditkarten blockieren
    mcp:
      auto_approve_requires_allowlist: true
      risky_tool_name_regex: "(?i)(create|update|delete|...)"

  internal_support:
    pii:
      email: mask
      phone: mask
      credit_card: mask    # Nur maskieren, nicht blockieren
    mcp:
      auto_approve_requires_allowlist: true
      risky_tool_name_regex: "(?i)(delete|remove|...)"

  ops_agent:
    pii:
      email: mask
      phone: mask
      credit_card: block
    mcp:
      auto_approve_requires_allowlist: true
      risky_tool_name_regex: "(?i)(create|update|delete|...)"
```

**PII-Modi:**
- `mask` - Maskiert sensible Daten (z.B. `<EMAIL_ADDRESS>`)
- `block` - Blockiert Requests mit sensiblen Daten

**Preset-Auswahl:**
- Via Request-Metadata: `metadata.ai_shield_preset` oder `metadata.preset`
- Fallback: `default_preset` aus YAML

---

## Features

### 1. Prompt-Injection-Erkennung

Das System erkennt verdächtige Eingaben basierend auf Signalen:

- "ignore previous instructions"
- "disregard system prompt"
- "reveal system prompt"
- "jailbreak"
- "developer mode"
- etc.

**Scoring:**
- Jedes Signal: +2 Punkte
- Code-Blöcke (```): +1 Punkt
- "system prompt" Erwähnung: +1 Punkt

**Blockierung:**
- Standard-Threshold: 6 Punkte (konfigurierbar pro Preset)
- Blockierte Requests werden mit Fehlermeldung zurückgegeben

### 2. PII-Masking

Automatische Erkennung und Maskierung von:

- **E-Mails**: Regex-basierte Erkennung
- **Telefonnummern**: Internationale Formate
- **Kreditkarten**: Luhn-Algorithmus-Validierung

**Beispiel:**
```
Input:  "Contact me at john@example.com or 555-1234"
Output: "Contact me at <EMAIL_ADDRESS> or <PHONE_NUMBER>"
```

### 3. MCP-Tool-Policy-Enforcement

**Tool-Kategorisierung:**
- `read` - Nur-Lese-Operationen (auto-approve)
- `write` - Schreib-Operationen (HITL erforderlich)
- `dangerous` - Gefährliche Operationen (blockiert)

**Kategorisierungslogik:**
- Gefährliche Keywords: `delete`, `remove`, `drop`, `destroy`, `revoke`, `shutdown`, `terminate`, `kill`, `rm`, `wipe`
- Schreib-Keywords: `create`, `update`, `set`, `write`, `send`, `post`, `put`, `patch`, `run`, `exec`, `apply`, `deploy`, `transfer`, `charge`, `payment`
- Poison-Patterns: `ignore previous`, `system prompt`, `exfiltrat`, `secret`, `apikey`, `token`, `credential`

**Policy-Enforcement:**
- `read` Tools: Automatisch erlaubt (wenn Allowlist vorhanden)
- `write` Tools: Erfordern Human-in-the-Loop (HITL)
- `dangerous` Tools: Werden blockiert

### 4. MCP-Server-Registry

Die Control Plane verwaltet eine zentrale Registry von MCP-Servern:

**Registry-Struktur:**
```json
{
  "servers": {
    "server_id": {
      "server_id": "my-mcp-server",
      "url": "http://localhost:9000/mcp",
      "transport": "streamable_http",
      "auth_type": "none",
      "headers": {},
      "preset": "read_only",
      "pinned_tools_hash": "sha256...",
      "tool_categories": {
        "tool_name": "read|write|dangerous"
      },
      "auto_approve_tools": ["tool1", "tool2"],
      "hitl_tools": ["tool3", "tool4"],
      "allowed_params": {
        "tool_name": ["param1", "param2"]
      },
      "pinned_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

---

## API-Referenz

### Control Plane API

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

#### Registry abrufen

```http
GET /v1/mcp/registry
Headers:
  x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
```

**Response:**
```json
{
  "servers": {
    "server_id": { ... }
  }
}
```

#### MCP-Server registrieren

```http
POST /v1/mcp/registry
Headers:
  x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
Body:
{
  "server_id": "my-mcp-server",
  "url": "http://localhost:9000/mcp",
  "transport": "streamable_http",
  "auth_type": "none",
  "headers": {},
  "preset": "read_only"
}
```

**Response:**
```json
{
  "ok": true,
  "server_id": "my-mcp-server"
}
```

#### Tools pinnen (kategorisieren)

```http
POST /v1/mcp/pin/{server_id}
Headers:
  x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
```

**Response:**
```json
{
  "server_id": "my-mcp-server",
  "pinned_tools_hash": "sha256...",
  "tool_count": 42,
  "pinned_at": "2024-01-01T00:00:00Z"
}
```

**Funktionalität:**
1. Ruft Tools vom Gateway ab
2. Kategorisiert Tools (read/write/dangerous)
3. Extrahiert erlaubte Parameter
4. Speichert in Registry

#### LiteLLM-Konfiguration exportieren

```http
GET /v1/mcp/litellm-snippet
Headers:
  x-ai-shield-admin-key: <CONTROL_PLANE_ADMIN_KEY>
```

**Response:**
```json
{
  "yaml": "mcp_servers:\n  server_id:\n    url: \"...\"\n    ..."
}
```

### Gateway API

Das Gateway verwendet die Standard-LiteLLM-API:

```http
POST /v1/chat/completions
Headers:
  Authorization: Bearer <LITELLM_MASTER_KEY>
Body:
{
  "model": "gpt-4o-mini",
  "messages": [...],
  "metadata": {
    "ai_shield_preset": "public_website"
  },
  "tools": [...]
}
```

**Sicherheitsprüfungen:**
- Prompt-Injection-Erkennung (Pre-Call)
- PII-Masking (Pre-Call)
- MCP-Tool-Filterung (Pre-Call)
- Audit-Logging (Post-Call)

---

## Best Practices

### 1. Preset-Auswahl

- **Public Website**: Strengste Sicherheit, blockiert Kreditkarten
- **Internal Support**: Moderate Sicherheit, maskiert PII
- **Ops Agent**: Erlaubt mehr Operationen, aber blockiert gefährliche

### 2. MCP-Server-Registrierung

1. Server in Control Plane registrieren
2. Tools pinnen (automatische Kategorisierung)
3. Preset auswählen (`read_only` für sichere Server)
4. LiteLLM-Konfiguration exportieren und verwenden

### 3. Tool-Policy-Konfiguration

- **Read-Only Preset**: Nur `read` Tools werden auto-approved
- **Standard Preset**: `read` und `write` Tools erlaubt, `dangerous` blockiert
- **Custom Presets**: Eigene Regex-Patterns für `risky_tool_name_regex`

### 4. Monitoring & Audit

- Alle Blockierungen werden geloggt (JSON-Format)
- Request-IDs werden generiert für Traceability
- Injection-Scores werden aufgezeichnet

### 5. Fehlerbehandlung

- Gateway läuft weiter, auch wenn Control Plane nicht erreichbar ist
- Fallback auf Standard-Preset, wenn Registry nicht verfügbar
- Graceful Degradation bei MCP-Server-Fehlern

---

## Sicherheitshinweise

⚠️ **Wichtig:**
- `CONTROL_PLANE_ADMIN_KEY` muss stark sein (mindestens 32 Zeichen)
- `LITELLM_MASTER_KEY` sollte nicht in Code committed werden
- Registry-Dateien enthalten sensible Informationen (Tool-Namen, URLs)
- Gateway sollte hinter einem Reverse-Proxy mit TLS laufen

---

## Troubleshooting

### Gateway blockiert legitime Requests

- Prüfe Injection-Score in Logs
- Passe Threshold in Preset-Konfiguration an
- Prüfe PII-Erkennung (kann false positives haben)

### MCP-Tools werden nicht gefiltert

- Prüfe Registry-Pfad (`AI_SHIELD_REGISTRY_PATH`)
- Stelle sicher, dass Tools gepinnt wurden
- Prüfe Preset-Konfiguration

### Control Plane nicht erreichbar

- Prüfe Port-Konfiguration
- Prüfe Docker-Container-Status
- Prüfe Logs: `docker-compose logs control-plane`

---

## Weitere Informationen

### Dokumentation

- **[System-Dokumentation](./SYSTEM_DOCUMENTATION.md)** - Vollständige System-Dokumentation
- **[Sicherheit & Installation](./security.md)** - Erweiterungen und Verbesserungen

### Externe Ressourcen

- **LiteLLM Dokumentation**: https://docs.litellm.ai/
- **Langfuse Dokumentation**: https://langfuse.com/docs
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Presidio Dokumentation**: https://microsoft.github.io/presidio/
- **OpenTelemetry**: https://opentelemetry.io/

### Konfigurationsdateien

- **Gateway Config**: `apps/gateway/config.yaml`
- **Policy Presets**: `apps/gateway/policies/presets.yaml`
- **OpenTelemetry**: `deploy/otel-collector.yaml`
- **Nginx**: `deploy/nginx.conf`
- **Prometheus**: `deploy/prometheus.yml`

