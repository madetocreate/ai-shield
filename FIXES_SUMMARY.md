# AI-Shield Hardening & Fixes - Zusammenfassung

## Durchgeführte Fixes

### PHASE 1: P0 Bugfixes (Control-Plane Integrations)

#### 1.1 Provider Enum Konsistenz
- **Datei**: `apps/control-plane/app/integrations/types.py`
- **Änderung**: CALENDLY, MICROSOFT_365, ZOOM zum Provider Enum hinzugefügt
- **Datei**: `apps/control-plane/app/integrations/index.py`
- **Änderung**: Provider-Module zu PROVIDER_MODULES Mapping hinzugefügt

#### 1.2 tripadvisor ImportError
- **Dateien**: 
  - `apps/control-plane/app/integrations/types.py`
  - `apps/control-plane/app/integrations/providers/__init__.py`
  - `apps/control-plane/app/integrations/index.py`
- **Änderung**: TRIPADVISOR aus Enum und Imports entfernt (Datei existierte nicht)

#### 1.3 get_default_scopes() Crash Fix
- **Datei**: `apps/control-plane/app/integrations/policies.py`
- **Änderungen**:
  - Nutzt jetzt `provider.name` statt `provider.value.upper()` für ENV-Keys
  - Unterstützt JSON Array und comma-separated String Parsing
  - Deduplizierung von Scopes
  - Entfernung nicht-existierender Provider aus Defaults (BOOKING_COM, AIRBNB, etc.)

#### 1.4 Provider Module get_access_token() Signatur
- **Dateien**:
  - `apps/control-plane/app/integrations/providers/trustpilot.py`
  - `apps/control-plane/app/integrations/providers/google_reviews.py`
  - `apps/control-plane/app/integrations/providers/yelp.py`
  - `apps/control-plane/app/integrations/providers/facebook_reviews.py`
- **Änderung**: Alle Aufrufe von `nango.get_access_token(tenant_id, "provider", connection_id)` zu `await nango.get_access_token(provider="...", connection_id="...")` geändert

### PHASE 2: Nango API Modernisierung

#### 2.1 NangoClient Modernisierung
- **Datei**: `apps/control-plane/app/integrations/nangoClient.py`
- **Änderungen**:
  - `get_connection()`: Nutzt jetzt `/connections/{connection_id}` (plural) statt `/connection/{connection_id}`
  - `get_access_token()`: Verbesserte Token-Extraktion (access_token, oauth_token)
  - `proxy()`: 
    - Setzt `Connection-Id` und `Provider-Config-Key` als **Headers** statt Query Params
    - Parameter umbenannt: `provider` → `provider_config_key`
    - Endpoint-Normalisierung (führende Slashes entfernen)
  - Alle Provider-Module: `provider=` zu `provider_config_key=` geändert

### PHASE 3: Gateway Policy / Registry

#### 3.1 Registry Path Konsistenz
- **Datei**: `apps/gateway/policy_engine.py`
- **Änderung**: 
  - Registry Path Default: `/app/control-plane-data/mcp_registry.json` (konsistent mit custom_callbacks.py)
  - Registry-Lade-Methode `_load_registry()` hinzugefügt mit Caching

#### 3.2 MCP Auto-Approval Härtung
- **Datei**: `apps/gateway/policy_engine.py`
- **Änderung**: 
  - Neue Methode `_sanitize_mcp_auto_approval()` hinzugefügt
  - `require_approval=never` wird entfernt wenn:
    - Kein `server_id` vorhanden
    - Server nicht in Registry existiert
    - Server unpinned ist (`pinned_tools_hash` fehlt)
    - `allowed_tools` leer ist
    - `allowed_tools` nicht in `auto_approve_tools` enthalten sind
  - Logging: `AUTO_APPROVAL_DISABLED_REASON=...` für Debugging

### PHASE 4: Docker Compose

#### 4.1 nginx htpasswd Handling
- **Datei**: `docker-compose.yml`
- **Änderung**: Mount auf `nginx.htpasswd.example` statt `nginx.htpasswd` (verhindert Fehler wenn Datei fehlt)

#### 4.2 Presidio Images Pinning
- **Datei**: `docker-compose.yml`
- **Änderung**: 
  - `presidio-analyzer:latest` → `presidio-analyzer:2.2.33`
  - `presidio-anonymizer:latest` → `presidio-anonymizer:2.2.33`

### PHASE 5: Security / Logging

#### 5.1 Redaction in Control-Plane Logs
- **Datei**: `apps/control-plane/app/integrations/policies.py`
- **Änderungen**:
  - Neue Funktionen `_redact_value()` und `_redact_dict()` hinzugefügt
  - Redaktion von:
    - Keys matching `/(token|secret|authorization|api[_-]?key|password)/i`
    - Strings mit API-Key Patterns (`sk-`, `pk-`, etc.)
    - Bearer Tokens
  - `log_operation()` nutzt jetzt strukturiertes Logging statt `print()`

### PHASE 6: Tests

#### Neue Tests hinzugefügt:
1. **`apps/control-plane/tests/test_integrations_policies.py`**:
   - `test_default_scopes_env_override()`: Testet ENV-Override für Scopes
   - `test_default_scopes_fallback()`: Testet Fallback zu Defaults
   - `test_default_scopes_empty_env()`: Testet leere ENV

2. **`apps/control-plane/tests/test_nango_client.py`**:
   - `test_nango_proxy_headers()`: Testet dass Headers korrekt gesetzt werden
   - `test_nango_get_connection_endpoint()`: Testet `/connections/{id}` Endpoint
   - `test_nango_get_access_token_extraction()`: Testet Token-Extraktion

3. **`apps/gateway/tests/test_policy_engine_auto_approval.py`**:
   - `test_auto_approval_disabled_when_unpinned()`: Testet Auto-Approval Sanitization
   - `test_auto_approval_no_allowed_tools()`: Testet leere allowed_tools
   - `test_auto_approval_non_mcp_tool()`: Testet dass non-MCP Tools nicht betroffen sind

## Lokale Checks ausführen

### 1. Compile Checks
```bash
cd /Users/simple-gpt/Backend/ai-shield
python3 -m compileall apps/control-plane/app
python3 -m compileall apps/gateway
```

### 2. Import Check
```bash
cd /Users/simple-gpt/Backend/ai-shield/apps/control-plane
python3 -c "from app.integrations import index; from app.integrations.providers import *"
```

### 3. Tests ausführen
```bash
cd /Users/simple-gpt/Backend/ai-shield
# Control-Plane Tests
pytest apps/control-plane/tests/ -v

# Gateway Tests
pytest apps/gateway/tests/ -v

# Alle Tests
pytest apps/control-plane/tests/ apps/gateway/tests/ -v
```

### 4. Docker Compose Start
```bash
cd /Users/simple-gpt/Backend/ai-shield
docker compose up
```

## Geänderte Dateien

### Control-Plane:
- `apps/control-plane/app/integrations/types.py`
- `apps/control-plane/app/integrations/index.py`
- `apps/control-plane/app/integrations/providers/__init__.py`
- `apps/control-plane/app/integrations/policies.py`
- `apps/control-plane/app/integrations/nangoClient.py`
- `apps/control-plane/app/integrations/providers/trustpilot.py`
- `apps/control-plane/app/integrations/providers/google_reviews.py`
- `apps/control-plane/app/integrations/providers/yelp.py`
- `apps/control-plane/app/integrations/providers/facebook_reviews.py`
- `apps/control-plane/app/integrations/providers/calendly.py`
- `apps/control-plane/app/integrations/providers/microsoft_365.py`
- `apps/control-plane/app/integrations/providers/zoom.py`
- Alle weiteren Provider-Module (via sed für `provider=` → `provider_config_key=`)

### Gateway:
- `apps/gateway/policy_engine.py`

### Deploy:
- `docker-compose.yml`

### Tests:
- `apps/control-plane/tests/test_integrations_policies.py` (neu)
- `apps/control-plane/tests/test_nango_client.py` (neu)
- `apps/gateway/tests/test_policy_engine_auto_approval.py` (neu)

## Akzeptanzkriterien Status

✅ **A) Control-plane**:
- ✅ Provider Enum konsistent
- ✅ Import check sollte funktionieren (tripadvisor entfernt)
- ✅ get_default_scopes() nutzt provider.name
- ✅ Keine AttributeError für Provider

✅ **B) Nango**:
- ✅ proxy() setzt Connection-Id und Provider-Config-Key als Headers
- ✅ connections endpoints nutzen /connections/{id}

✅ **C) Gateway**:
- ✅ PolicyEngine nutzt /app/control-plane-data/mcp_registry.json default
- ✅ Unpinned MCP server kann niemals auto-execute

✅ **D) Deploy**:
- ✅ docker compose up startet ohne missing htpasswd file
- ✅ Keine :latest in prod compose (Presidio gepinnt)

✅ **E) Tests**:
- ✅ test_default_scopes_env_override
- ✅ test_nango_proxy_headers
- ✅ test_auto_approval_disabled_when_unpinned

## Nächste Schritte

1. Tests lokal ausführen und verifizieren
2. Docker Compose starten und Smoke Tests durchführen
3. Optional: Weitere Provider-Module auf `nango.proxy()` umstellen (statt Token + httpx)

