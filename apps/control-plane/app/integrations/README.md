# Integrations Module

Nango-basierte OAuth-Integrationen für AI Shield.

## Struktur

```
integrations/
├── __init__.py          # Module init
├── types.py             # Type definitions (Provider, Connection, ApprovalRequest)
├── nangoClient.py       # Nango HTTP Client Wrapper
├── connectionsRepo.py   # Connection Storage (aktuell in-memory, später DB)
├── policies.py          # Read/Write Gating + HITL Policies
├── api.py               # FastAPI Router für Connect/Disconnect/Status
├── approvals.py         # Approval Queue API
├── index.py             # Provider Registry
└── providers/
    ├── __init__.py
    ├── google.py         # Google Calendar Integration
    ├── shopify.py        # Shopify Integration
    ├── woocommerce.py    # WooCommerce Integration
    └── whatsapp.py       # WhatsApp (Meta) Integration
```

## Features

### ✅ Implementiert (Skeleton)

- **Connection Management**: Connect/Disconnect/Status Endpoints
- **Provider Wrapper**: Alle Provider-Funktionen existieren (Google, Shopify, WooCommerce, WhatsApp)
- **Approval Flow**: Write-Operationen erfordern Genehmigung
- **Policies**: Automatische Erkennung von Read/Write-Operationen
- **Audit Logging**: Operationen werden geloggt (wenn enabled)

### 🔄 Noch zu implementieren

- **OAuth Flow**: Echte Nango OAuth-URLs generieren
- **Database**: Connections und Approvals in DB speichern (aktuell in-memory)
- **Webhook Handling**: Nango Webhooks empfangen und verarbeiten
- **Token Refresh**: Automatisches Token-Refresh via Nango
- **Provider Credentials**: Echte Client IDs/Secrets in Nango konfigurieren

## API Endpoints

### Connections

- `GET /v1/integrations/` - Liste aller Connections
- `POST /v1/integrations/{provider}/connect` - OAuth-Verbindung initiieren
- `POST /v1/integrations/{provider}/disconnect` - Verbindung trennen
- `GET /v1/integrations/{provider}/status` - Connection-Status abfragen
- `POST /v1/integrations/{provider}/callback` - OAuth-Callback (von Nango)

### Approvals

- `GET /v1/integrations/approvals` - Liste aller Approval Requests
- `POST /v1/integrations/approvals/{request_id}/approve` - Request genehmigen & ausführen
- `POST /v1/integrations/approvals/{request_id}/reject` - Request ablehnen

## Provider-Funktionen

### Google Calendar

- `calendar_find_slots()` - Verfügbare Zeitslots finden (read)
- `calendar_create_event()` - Event erstellen (write → approval)

### Shopify

- `orders_get_status()` - Bestellstatus abfragen (read)
- `draft_order_create()` - Draft Order erstellen (write → approval)

### WooCommerce

- `orders_get_status()` - Bestellstatus abfragen (read)
- `customer_tag()` - Kunde taggen (write → approval)

### WhatsApp

- `messages_send()` - Nachricht senden (write → approval)
- `webhook_receive()` - Webhook empfangen

## Environment Variables

Siehe `.env.example` im Hauptprojekt:

```bash
# Nango Configuration
NANGO_BASE_URL=http://127.0.0.1:3003
NANGO_API_KEY=REPLACE_ME
NANGO_WEBHOOK_SECRET=REPLACE_ME

# Default Scopes
INTEGRATIONS_DEFAULT_SCOPES_GOOGLE=calendar.readonly
INTEGRATIONS_DEFAULT_SCOPES_SHOPIFY=read_orders,read_customers
INTEGRATIONS_DEFAULT_SCOPES_META=whatsapp_business_messaging
INTEGRATIONS_DEFAULT_SCOPES_WOOCOMMERCE=read

# Safety Settings
INTEGRATIONS_WRITE_REQUIRES_APPROVAL=1
INTEGRATIONS_AUDIT_LOG=1
```

## Nächste Schritte

1. **Nango starten**: `cd ~/nango-auth && docker compose up -d`
2. **Provider konfigurieren**: In Nango UI oder via ENV Provider-Credentials eintragen
3. **OAuth URLs generieren**: `nangoClient.get_auth_url()` implementieren
4. **Database Migration**: Connections und Approvals in DB migrieren
5. **Webhook Endpoint**: `/v1/integrations/webhook` für Nango Webhooks

## Frontend

Frontend-Komponenten befinden sich in:
- `src/components/integrations/IntegrationsDashboard.tsx` - Haupt-UI für Integrationen
- `src/components/integrations/ApprovalQueue.tsx` - Approval Queue UI
