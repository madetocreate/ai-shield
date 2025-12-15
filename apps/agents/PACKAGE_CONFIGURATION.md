# Paket-Konfiguration

Diese Dokumentation beschreibt, wie die Branchen-Pakete konfiguriert und aktiviert werden.

---

## Vertical Package Manifest

Das `vertical_package_manifest` System ermöglicht es, Branchen-Pakete pro Account zu aktivieren und zu konfigurieren.

### Beispiel: Gastronomie-Paket aktivieren

```python
from apps.agents.shared.vertical_package_manifest import (
    VerticalPackageManifest,
    PackageType,
    IntegrationConfig,
    PolicyConfig,
    get_registry
)

# Manifest erstellen
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
    integrations=[
        IntegrationConfig(
            integration_id="opentable",
            enabled=True,
            config={
                "api_key": "...",
                "restaurant_id": "..."
            }
        ),
        IntegrationConfig(
            integration_id="toast_pos",
            enabled=True,
            config={
                "api_key": "...",
                "location_id": "..."
            }
        ),
    ],
    policies=PolicyConfig(
        preset="public_website",
        pii_mode="mask",
        require_consent=True,
        retention_days=90
    ),
    metadata={
        "restaurant_name": "Beispiel Restaurant",
        "cuisine_type": "italian",
        "opening_hours": {...}
    }
)

# Speichern
registry = get_registry()
registry.save_manifest(manifest)
```

### Beispiel: Praxis-Paket aktivieren

```python
manifest = VerticalPackageManifest(
    package_type=PackageType.PRACTICE,
    account_id="praxis-456",
    enabled_agents=[
        "practice_supervisor_agent",
        "practice_phone_reception_agent",
        "practice_appointment_reminder_agent",
        "practice_patient_intake_forms_agent",
        "practice_admin_requests_agent",
        "healthcare_privacy_guard_agent",
    ],
    integrations=[
        IntegrationConfig(
            integration_id="doctolib",
            enabled=True,
            config={
                "api_key": "...",
                "practice_id": "..."
            }
        ),
        IntegrationConfig(
            integration_id="pvs",
            enabled=True,
            config={
                "system": "medatixx",
                "api_endpoint": "..."
            }
        ),
    ],
    policies=PolicyConfig(
        preset="public_website",
        pii_mode="block",  # Strenger für Gesundheitsdaten
        require_consent=True,
        retention_days=365,  # 1 Jahr für Gesundheitsdaten
        custom_rules={
            "require_explicit_consent_for_phi": True,
            "minimal_data_collection": True
        }
    ),
    metadata={
        "practice_name": "Beispiel Praxis",
        "specialization": "general",
        "accepts_new_patients": True
    }
)

registry.save_manifest(manifest)
```

---

## Consent & Redaction Gateway

### Consent erteilen

```python
from apps.agents.shared.consent_and_redaction_gateway import (
    get_gateway,
    DataCategory
)

gateway = get_gateway()

# Consent für PII erteilen
consent = gateway.grant_consent(
    account_id="restaurant-123",
    user_id="user-789",
    category=DataCategory.PII,
    expires_in_days=90,
    purpose="Reservierungsverwaltung"
)

# Consent für PHI erteilen (Praxis)
consent = gateway.grant_consent(
    account_id="praxis-456",
    user_id="patient-101",
    category=DataCategory.PHI,
    expires_in_days=365,
    purpose="Terminverwaltung"
)
```

### Content redactieren

```python
# Content redactieren
redacted, categories = gateway.redact_content(
    content="Meine E-Mail ist max@example.com und meine Telefonnummer ist 0123456789",
    account_id="restaurant-123",
    user_id="user-789",
    require_consent=True
)

# Ergebnis:
# redacted = "Meine E-Mail ist [EMAIL] und meine Telefonnummer ist [PHONE]"
# categories = ["pii"]
```

### Retention-Policy setzen

```python
# Retention-Policy für Account setzen
gateway.set_retention_policy(
    account_id="praxis-456",
    days=365  # 1 Jahr für Gesundheitsdaten
)
```

---

## Handoff to Human Protocol

### Handoff auslösen

```python
from apps.agents.shared.handoff_to_human_protocol import (
    get_protocol,
    HandoffReason,
    HandoffPriority
)

protocol = get_protocol()

# Handoff bei Safety-Concern
handoff = protocol.should_handoff(
    account_id="praxis-456",
    user_id="patient-101",
    channel="phone",
    conversation_id="conv-123",
    reason=HandoffReason.SAFETY_CONCERN,
    context={
        "symptom": "Brustschmerz",
        "urgency": "high"
    }
)

if handoff:
    # Handoff wurde erstellt
    print(f"Handoff erforderlich: {handoff.summary}")
    print(f"Priorität: {handoff.priority}")
    print(f"Methode: {handoff.method}")
```

### Pending Handoffs abrufen

```python
# Alle ausstehenden Handoffs für Account
pending = protocol.get_pending_handoffs(
    account_id="praxis-456",
    priority=HandoffPriority.CRITICAL
)

for handoff in pending:
    print(f"{handoff.reason}: {handoff.summary}")
```

---

## Agent-Initialisierung

### Gastronomie-Agent initialisieren

```python
from apps.agents.gastronomy import (
    GastronomySupervisorAgent,
    RestaurantVoiceHostAgent
)

# Supervisor Agent
supervisor = GastronomySupervisorAgent(account_id="restaurant-123")

# Routing-Entscheidung
decision = supervisor.route_request(
    user_message="Ich möchte einen Tisch für morgen Abend reservieren",
    context={"channel": "phone"}
)

print(f"Intent: {decision.intent}")
print(f"Target Agent: {decision.target_agent}")
print(f"Confidence: {decision.confidence}")

# Voice Host Agent
voice_host = RestaurantVoiceHostAgent(
    account_id="restaurant-123",
    integration_agent=integration_agent  # Via Dependency Injection
)

# Reservierung verarbeiten
result = voice_host.handle_reservation_request(
    user_message="Tisch für 4 Personen am Samstag um 19 Uhr",
    context={"channel": "phone"}
)
```

### Praxis-Agent initialisieren

```python
from apps.agents.practice import (
    PracticeSupervisorAgent,
    PracticePhoneReceptionAgent,
    HealthcarePrivacyGuardAgent
)

# Supervisor Agent
supervisor = PracticeSupervisorAgent(account_id="praxis-456")

# Routing mit Safety-Check
decision = supervisor.route_request(
    user_message="Ich habe starke Brustschmerzen",
    context={"channel": "phone"}
)

print(f"Intent: {decision.intent}")
print(f"Requires Safety Check: {decision.requires_safety_check}")

# Phone Reception Agent
reception = PracticePhoneReceptionAgent(
    account_id="praxis-456",
    integration_agent=integration_agent,
    healthcare_privacy_guard=privacy_guard
)

# Safety Routing
safety_result = reception.handle_safety_routing(
    user_message="Ich habe starke Brustschmerzen",
    context={"channel": "phone"}
)

if safety_result["action"] == "emergency":
    print("NOTFALL - Eskalation erforderlich")

# Privacy Guard
privacy_guard = HealthcarePrivacyGuardAgent(
    account_id="praxis-456",
    consent_gateway=consent_gateway
)

# Request validieren
validation = privacy_guard.validate_request(
    use_case="appointment",
    collected_data={
        "name": "Max Mustermann",
        "phone": "0123456789",
        "date": "2024-01-15",
        "time": "10:00"
    },
    content="Ich möchte einen Termin"
)

if not validation.allowed:
    print(f"Privacy-Verletzung: {validation.message}")
```

---

## Integration mit Global Orchestrator

Der `global_orchestrator_agent` muss die Paket-Manifeste prüfen und entsprechend routen:

```python
# Pseudo-Code für Global Orchestrator
def route_request(account_id, user_message, context):
    # Manifest laden
    registry = get_registry()
    manifest = registry.get_manifest(account_id)
    
    if not manifest:
        # Fallback zu Standard-Routing
        return default_routing(user_message, context)
    
    # Basierend auf Package-Type routen
    if manifest.package_type == PackageType.GASTRONOMY:
        supervisor = GastronomySupervisorAgent(account_id)
        decision = supervisor.route_request(user_message, context)
        return route_to_agent(decision.target_agent, user_message, context)
    
    elif manifest.package_type == PackageType.PRACTICE:
        supervisor = PracticeSupervisorAgent(account_id)
        decision = supervisor.route_request(user_message, context)
        
        # Safety-Check wenn erforderlich
        if decision.requires_safety_check:
            privacy_guard = HealthcarePrivacyGuardAgent(account_id)
            validation = privacy_guard.validate_request(...)
            if not validation.allowed:
                # Eskalieren
                return escalate_to_human(...)
        
        return route_to_agent(decision.target_agent, user_message, context)
```

---

## Best Practices

1. **Datensparsamkeit**: Immer nur minimale notwendige Daten sammeln
2. **Consent-Management**: Consent vor Datenerhebung prüfen
3. **Redaction**: PII/PHI vor Memory/Logs redactieren
4. **Safety-First**: Bei medizinischen Inhalten immer Safety-Check
5. **Human Handoff**: Bei Unsicherheit eskalieren
6. **Retention**: Daten nach Retention-Policy löschen
7. **Testing**: Pakete isoliert testen vor Rollout
