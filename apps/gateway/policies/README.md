# AI-Shield Policy System

## Übersicht

Das AI-Shield Policy System bietet eine produktionsreife Schicht für Stabilität und Verkaufbarkeit. Es besteht aus:

1. **Policy Packs**: Versionierte Policy-Pakete für verschiedene Use Cases
2. **Compatibility Modes**: observe/warn/block Modi für flexible Deployment-Strategien
3. **Test Harness**: Automatisierte Tests für Policy-Validierung
4. **Observability**: Strukturierte Logs, Metrics und Correlation IDs

## Policy Packs

Policy Packs sind versionierte Pakete unter `/policies/packs/*`. Jedes Pack enthält:

- `policy.yaml`: Policy-Konfiguration
- `README.md`: Dokumentation und Changelog

### Verfügbare Packs

#### `kmu_standard`
Standard-Policy für kleine und mittlere Unternehmen. Moderate Sicherheit mit guter UX.

**Features:**
- PII-Maskierung (E-Mail, Telefon)
- Kreditkarten-Blockierung
- Prompt-Injection-Schutz (Threshold 6)
- Compatibility Mode: `warn` (Standard)

#### `healthcare_light`
Lightweight Healthcare-Policy für nicht-kritische Anwendungen. Strikter Datenschutz.

**Features:**
- Strikte PII-Blockierung (alle Typen)
- Erweiterte Prompt-Injection-Erkennung (Threshold 4)
- Strenge Tool-Permissions
- Compatibility Mode: `block` (Standard)

## Compatibility Modes

Compatibility Modes bestimmen, wie Policy-Verletzungen behandelt werden:

### `observe`
- **Verhalten**: Niemals blockieren, nur loggen
- **Use Case**: Monitoring und Testing
- **Response**: Immer `allow`, auch bei Verletzungen

### `warn`
- **Verhalten**: Non-breaking Warnings in Response-Headers/Metadata
- **Use Case**: Graduelle Einführung, UX-freundlich
- **Response**: `warn` statt `block`, Request wird durchgelassen

### `block`
- **Verhalten**: Harte Ablehnung mit stabilen Error Codes
- **Use Case**: Production mit strikten Sicherheitsanforderungen
- **Response**: `block` bei Verletzungen, Request wird abgelehnt

## Konfiguration

### Per Request (Metadata)

```python
{
  "messages": [...],
  "metadata": {
    "ai_shield_preset": "kmu_standard",
    "compatibility_mode": "warn",
    "tenant_id": "tenant-123"
  }
}
```

### Per Environment Variable

```bash
# Default Preset
AI_SHIELD_PRESET_DEFAULT=kmu_standard

# Default Compatibility Mode
AI_SHIELD_COMPATIBILITY_MODE=block

# Policy Path
AI_SHIELD_POLICY_PATH=/app/policies/presets.yaml

# Packs Path
AI_SHIELD_PACKS_PATH=/app/policies/packs
```

### Per Tenant (Override)

Tenant-spezifische Overrides können über die Control-Plane API konfiguriert werden (zukünftig).

## Test Harness

### Test-Dateien

Tests befinden sich unter `/policies/tests/*.json`:

- `test_pii_detection.json`: PII-Erkennung Tests
- `test_prompt_injection.json`: Prompt-Injection Tests
- `test_tool_permissions.json`: Tool-Permission Tests

### Expected Results

Expected Results befinden sich unter `/policies/expected/<pack>/*.json`:

- `expected/kmu_standard/test_pii_detection.json`
- `expected/healthcare_light/test_pii_detection.json`
- etc.

### Test-Script

```bash
# Alle Tests für alle Packs
python scripts/run_policy_tests.py

# Tests für spezifisches Pack
python scripts/run_policy_tests.py --pack kmu_standard

# Spezifischer Test
python scripts/run_policy_tests.py --test test_pii_detection
```

## Observability

### Correlation ID

Jede Policy-Entscheidung erhält eine `correlation_id`, die:

- In allen Logs enthalten ist
- Als Response-Header `X-Correlation-ID` zurückgegeben wird
- Für Request-Tracing verwendet werden kann

### Strukturierte Logs

Alle Logs enthalten strukturierte Felder:

```json
{
  "event": "policy_decision",
  "correlation_id": "uuid-here",
  "tenant_id": "tenant-123",
  "decision": "block",
  "reason_codes": ["prompt_injection_detected"],
  "rule_triggers": [...],
  "decision_time_ms": 2.5
}
```

### Metrics

Metrics werden über `PolicyEngine.get_metrics()` bereitgestellt:

```python
from policy_engine import get_policy_engine

engine = get_policy_engine()
metrics = engine.get_metrics()

# Output:
# {
#   "decision_count": {"allow": 100, "block": 5, "warn": 10},
#   "reason_code_count": {"prompt_injection_detected": 3, ...},
#   "decision_time_ms": {"count": 115, "avg": 2.1, "p95": 5.0, ...}
# }
```

### Response Headers

Bei erfolgreichen Requests werden folgende Header gesetzt:

- `X-Correlation-ID`: Correlation ID für Tracing
- `X-AI-Shield-Warnings`: JSON-Array von Warnings (wenn `warn` Mode)

## Pipeline

Die Policy Engine folgt dieser Pipeline:

1. **Normalize**: Request normalisieren, Correlation ID generieren
2. **Classify**: Text extrahieren, PII erkennen, Request klassifizieren
3. **Policy**: Policy-Regeln evaluieren, Decision treffen
4. **Redact**: Request sanitizen (PII maskieren) falls nötig
5. **Route**: Compatibility Mode anwenden (observe/warn/block)
6. **Log & Metrics**: Strukturiertes Logging und Metrics aufzeichnen

## Erweiterung

### Neues Policy Pack erstellen

1. Erstelle Verzeichnis: `/policies/packs/<pack_name>/`
2. Erstelle `policy.yaml` mit Policy-Konfiguration
3. Erstelle `README.md` mit Dokumentation
4. Füge Expected Results hinzu: `/policies/expected/<pack_name>/*.json`

### Neue Policy-Regel hinzufügen

1. Erweitere `PolicyEngine._evaluate_policy()` in `policy_engine.py`
2. Füge Reason Code hinzu
3. Erstelle Test-Cases in `/policies/tests/`
4. Füge Expected Results hinzu

## Best Practices

1. **Production**: Verwende `compatibility_mode: block` für strikte Sicherheit
2. **Testing**: Verwende `compatibility_mode: observe` für Monitoring
3. **Graduelle Einführung**: Starte mit `warn`, wechsle zu `block` nach Validierung
4. **Tenant-Isolation**: Nutze `tenant_id` für Multi-Tenant-Szenarien
5. **Monitoring**: Überwache Metrics regelmäßig, besonders `decision_time_ms`

