# Integration Guide - Branchen-Pakete

Dieser Guide beschreibt, wie die Branchen-Pakete in das bestehende System integriert werden.

---

## 🏗️ Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│              Global Orchestrator Agent                   │
│  (Prüft Package Manifest → Routet zu Vertical Router)  │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Gastronomy   │  │ Practice     │
│ Supervisor  │  │ Supervisor   │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Specialized  │  │ Specialized  │
│ Agents       │  │ Agents       │
└──────────────┘  └──────────────┘
```

---

## 🔧 Integration Steps

### 1. Agent Registry initialisieren

Die Agent Registry registriert automatisch alle Agents beim ersten Import:

```python
from apps.agents.core.agent_registry import get_registry

registry = get_registry()
print(registry.list_agents())  # Zeigt alle registrierten Agents
```

### 2. Package Manifest erstellen

```python
from apps.agents.shared.vertical_package_manifest import (
    VerticalPackageManifest,
    PackageType,
    PolicyConfig,
    get_registry
)

# Gastronomie-Paket aktivieren
manifest = VerticalPackageManifest(
    package_type=PackageType.GASTRONOMY,
    account_id="restaurant-123",
    enabled_agents=[
        "gastronomy_supervisor_agent",
        "restaurant_voice_host_agent",
        "restaurant_menu_allergen_agent",
        "restaurant_takeout_order_agent",
        "restaurant_reputation_agent",
        "restaurant_events_catering_agent",
    ],
    policies=PolicyConfig(
        preset="public_website",
        require_consent=True,
        retention_days=90
    )
)

registry = get_registry()
registry.save_manifest(manifest)
```

### 3. Global Orchestrator verwenden

```python
from apps.agents.core.global_orchestrator_agent import (
    get_orchestrator,
    RoutingRequest
)

orchestrator = get_orchestrator()

# Request routen
request = RoutingRequest(
    account_id="restaurant-123",
    user_message="Ich möchte einen Tisch reservieren",
    channel="phone",
    user_id="user-456",
    conversation_id="conv-789"
)

response = orchestrator.route(request)

# Agent verwenden
if response.agent_instance:
    result = response.agent_instance.handle_reservation_request(
        user_message=request.user_message,
        context={"channel": request.channel}
    )
```

---

## 🔌 Integration mit bestehenden Agents

### Dependency Injection

Die Agent Registry unterstützt automatische Dependency Injection:

```python
# Agent mit Dependencies holen
agent = registry.get_agent(
    "restaurant_voice_host_agent",
    account_id="restaurant-123",
    integration_agent=existing_integration_agent  # Optional: Override
)
```

### Bestehende Agents nutzen

Die neuen Agents können bestehende Agents als Dependencies nutzen:

```python
# Beispiel: Restaurant Events Catering Agent nutzt CRM Agent
from apps.agents.gastronomy import RestaurantEventsCateringAgent

agent = RestaurantEventsCateringAgent(
    account_id="restaurant-123",
    crm_agent=existing_crm_agent,  # Bestehender Agent
    proposal_agent=existing_proposal_agent,
    followup_agent=existing_followup_agent
)
```

---

## 🧪 Testing

### Tests ausführen

```bash
# Alle Tests
pytest apps/agents/tests/ -v

# Nur Gastronomie-Tests
pytest apps/agents/tests/test_gastronomy_agents.py -v

# Nur Praxis-Tests
pytest apps/agents/tests/test_practice_agents.py -v

# Shared Components
pytest apps/agents/tests/test_shared_components.py -v

# Global Orchestrator
pytest apps/agents/tests/test_global_orchestrator.py -v
```

### Test Coverage

```bash
pytest apps/agents/tests/ --cov=apps.agents --cov-report=html
```

---

## 📊 Monitoring & Observability

### Logging

Alle Agents loggen wichtige Events:

```python
import logging

logger = logging.getLogger("apps.agents")
logger.info("Agent action", extra={
    "account_id": account_id,
    "agent": "restaurant_voice_host_agent",
    "action": "reservation_request"
})
```

### Metrics

Wichtige Metrics zu tracken:
- Request-Rate pro Agent
- Routing-Entscheidungen
- Handoff-Rate
- Consent-Checks
- Error-Rate

---

## 🔒 Security & Compliance

### Consent-Management

```python
from apps.agents.shared.consent_and_redaction_gateway import (
    get_gateway,
    DataCategory
)

gateway = get_gateway()

# Consent erteilen
consent = gateway.grant_consent(
    account_id="restaurant-123",
    user_id="user-456",
    category=DataCategory.PII,
    expires_in_days=90
)

# Content redactieren
redacted, categories = gateway.redact_content(
    content="Meine E-Mail ist max@example.com",
    account_id="restaurant-123",
    user_id="user-456"
)
```

### Privacy Guard (Praxis)

```python
from apps.agents.practice import HealthcarePrivacyGuardAgent

privacy_guard = HealthcarePrivacyGuardAgent(
    account_id="praxis-456",
    consent_gateway=consent_gateway
)

# Request validieren
validation = privacy_guard.validate_request(
    use_case="appointment",
    collected_data={"name": "Max", "phone": "123"},
    content="Ich möchte einen Termin"
)

if not validation.allowed:
    # Eskalieren
    pass
```

---

## 🚨 Error Handling

### Handoff Protocol

```python
from apps.agents.shared.handoff_to_human_protocol import (
    get_protocol,
    HandoffReason
)

protocol = get_protocol()

# Handoff auslösen
handoff = protocol.should_handoff(
    account_id="praxis-456",
    user_id="patient-123",
    channel="phone",
    conversation_id="conv-789",
    reason=HandoffReason.SAFETY_CONCERN,
    context={"urgency": "high"}
)

if handoff:
    # Human übergeben
    transfer_to_human(handoff)
```

---

## 🔄 Workflow-Integration

### Beispiel: Reservierungs-Workflow

```python
# 1. Request kommt rein
request = RoutingRequest(
    account_id="restaurant-123",
    user_message="Ich möchte einen Tisch für morgen reservieren",
    channel="phone"
)

# 2. Orchestrator routet
response = orchestrator.route(request)

# 3. Agent verarbeitet
if response.target_agent == "restaurant_voice_host_agent":
    result = response.agent_instance.handle_reservation_request(
        user_message=request.user_message
    )
    
    # 4. Integration (Reservierungssystem)
    if result["status"] == "success":
        integration_agent.book_reservation(
            date=result["date"],
            time=result["time"],
            guests=result["guests"]
        )
    
    # 5. Bestätigung senden
    communications_supervisor.send_sms(
        phone=result["phone"],
        message=f"Reservierung bestätigt für {result['date']} um {result['time']}"
    )
```

---

## 📝 Best Practices

1. **Immer Package Manifest prüfen** vor Agent-Verwendung
2. **Consent-Management** für alle PII/PHI-Daten
3. **Error Handling** mit Handoff-Protocol
4. **Logging** für alle wichtigen Aktionen
5. **Testing** vor Production-Rollout
6. **Monitoring** für Performance und Errors

---

## 🐛 Troubleshooting

### Agent nicht gefunden

```python
# Prüfe Registry
registry = get_registry()
if not registry.is_registered("agent_name"):
    print("Agent nicht registriert")

# Prüfe Manifest
manifest = manifest_registry.get_manifest(account_id)
if not manifest.is_agent_enabled("agent_name"):
    print("Agent nicht aktiviert")
```

### Dependency-Fehler

```python
# Prüfe Dependencies
config = registry._agents.get("agent_name")
if config:
    print(f"Dependencies: {config.dependencies}")
```

### Routing-Fehler

```python
# Debug-Routing
response = orchestrator.route(request)
print(f"Target Agent: {response.target_agent}")
print(f"Metadata: {response.metadata}")
```

---

## 📚 Weitere Ressourcen

- [README.md](./README.md) - Übersicht
- [WORKFLOWS.md](./WORKFLOWS.md) - Workflow-Details
- [PACKAGE_CONFIGURATION.md](./PACKAGE_CONFIGURATION.md) - Konfiguration

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2024
