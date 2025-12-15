# Branchen-Pakete - Übersicht

Dieses Verzeichnis enthält die beiden Branchen-Pakete **Gastronomie** und **Praxis** mit allen benötigten Agents, Workflows und Shared Components.

---

## 📦 Paket-Übersicht

### 1. Gastronomie-Paket

**Zielbild:** Mehr Covers & weniger Stress - keine verpassten Anrufe, Reservierungen und Takeout laufen sauber durch.

**MVP Agents (6):**
- `gastronomy_supervisor_agent` - Vertical Router
- `restaurant_voice_host_agent` - Telefon-Host + Chat-Host
- `restaurant_menu_allergen_agent` - Menü + Allergene + Diäten
- `restaurant_takeout_order_agent` - Phone/SMS/Chat Besteller
- `restaurant_reputation_agent` - Reviews & Responses
- `restaurant_events_catering_agent` - Gruppen/Events/Catering → Deal

**V2 Agents (3):**
- `restaurant_shift_staffing_agent` - Schicht & Ausfälle
- `restaurant_inventory_procurement_agent` - Bestände & Nachbestellung
- `restaurant_daily_ops_report_agent` - Tagesabschlussbericht

**Workflows:** Siehe [WORKFLOWS.md](./WORKFLOWS.md#gastronomie-paket---workflows)

---

### 2. Praxis-Paket

**Zielbild:** AI-Rezeption + Patientenkommunikation - weniger verpasste Anrufe, weniger No-Shows, weniger Papierkram am Empfang.

**MVP Agents (6):**
- `practice_supervisor_agent` - Vertical Router
- `practice_phone_reception_agent` - AI Empfang am Telefon + Chat
- `practice_appointment_reminder_agent` - No-Show-Killer
- `practice_patient_intake_forms_agent` - Formulare & Vorbereitung
- `practice_admin_requests_agent` - Routine-Anliegen
- `healthcare_privacy_guard_agent` - Praxis-spezifische Hard Guardrails

**V2 Agents (3):**
- `practice_clinical_documentation_agent` - Für Behandler (Doku-Entwürfe)
- `practice_billing_insurance_agent` - Rechnungsfragen
- `practice_document_inbox_agent` - Fax/Briefe/Befunde

**Workflows:** Siehe [WORKFLOWS.md](./WORKFLOWS.md#praxis-paket---workflows)

---

## 🔧 Shared Components

Diese Komponenten werden **einmalig** gebaut und in beiden Paketen genutzt:

### 1. `vertical_package_manifest`
- Konfigurationssystem für Branchen-Pakete
- Ermöglicht austauschbare Paket-Konfigurationen ohne Hardcoding
- Definiert welche Agents, Integrationen und Policies aktiv sind

### 2. `consent_and_redaction_gateway`
- Pipeline-Komponente für PII/PHI-Schutz
- Consent-Management
- Automatische Redaction vor Memory/Logs
- Retention-Policy-Enforcement

### 3. `handoff_to_human_protocol`
- Einheitlicher Eskalationsstandard
- Entscheidet wann und wie von AI zu Human übergeben wird
- Priorisierung und Methoden-Auswahl

**Dokumentation:** Siehe [PACKAGE_CONFIGURATION.md](./PACKAGE_CONFIGURATION.md)

---

## 📋 Bestehende Agents (werden genutzt)

### Orchestrierung & Channels
- `global_orchestrator_agent` / Global Supervisor
- `communications_supervisor` (Routing über Kanäle inkl. Telefonie)
- `inbox_supervisor` (Multi-Channel Inbox)
- `website_workflow_agent` / `website_supervisor` (Website-Widget)

### Core / Knowledge / Safety
- `research_agent`, `web_verifier_agent`
- `memory_agent` + `knowledge_curator_agent` + `knowledge_base_agent`
- `document_intelligence_agent`
- Guardrails: `policy_guardrail_agent`, `output_safety_guardrail_agent` + `security_agent`

### Support / Marketing / Sales / Ops
- Support: `support_triage_agent`, `support_resolution_agent`
- Marketing: `content_generation_agent`, `personalization_agent`, `followup_agent`, `growth_experiment_agent`
- CRM: `crm_agent` + `contact_agent`, `deal_agent`, `proposal_agent`
- Backoffice: `integration_agent`, `meeting_prep_agent`, `data_quality_agent`

---

## 🚀 Quick Start

### 1. Paket aktivieren

```python
from apps.agents.shared.vertical_package_manifest import (
    VerticalPackageManifest,
    PackageType,
    get_registry
)

# Gastronomie-Paket aktivieren
manifest = VerticalPackageManifest(
    package_type=PackageType.GASTRONOMY,
    account_id="restaurant-123",
    enabled_agents=[
        "gastronomy_supervisor_agent",
        "restaurant_voice_host_agent",
        # ... weitere Agents
    ]
)

registry = get_registry()
registry.save_manifest(manifest)
```

### 2. Agent verwenden

```python
from apps.agents.gastronomy import GastronomySupervisorAgent

supervisor = GastronomySupervisorAgent(account_id="restaurant-123")
decision = supervisor.route_request(
    user_message="Ich möchte einen Tisch reservieren",
    context={"channel": "phone"}
)

print(f"Routen zu: {decision.target_agent}")
```

### 3. Workflow ausführen

Siehe [WORKFLOWS.md](./WORKFLOWS.md) für detaillierte Workflow-Beschreibungen.

---

## 📚 Dokumentation

- **[WORKFLOWS.md](./WORKFLOWS.md)** - Detaillierte Workflow-Beschreibungen für beide Pakete
- **[PACKAGE_CONFIGURATION.md](./PACKAGE_CONFIGURATION.md)** - Konfiguration und Integration
- **[shared/](./shared/)** - Shared Components Dokumentation

---

## 🏗️ Verzeichnisstruktur

```
apps/agents/
├── __init__.py
├── README.md (diese Datei)
├── WORKFLOWS.md
├── PACKAGE_CONFIGURATION.md
├── shared/
│   ├── __init__.py
│   ├── vertical_package_manifest.py
│   ├── consent_and_redaction_gateway.py
│   └── handoff_to_human_protocol.py
├── gastronomy/
│   ├── __init__.py
│   ├── gastronomy_supervisor_agent.py
│   ├── restaurant_voice_host_agent.py
│   ├── restaurant_menu_allergen_agent.py
│   ├── restaurant_takeout_order_agent.py
│   ├── restaurant_reputation_agent.py
│   └── restaurant_events_catering_agent.py
└── practice/
    ├── __init__.py
    ├── practice_supervisor_agent.py
    ├── practice_phone_reception_agent.py
    ├── practice_appointment_reminder_agent.py
    ├── practice_patient_intake_forms_agent.py
    ├── practice_admin_requests_agent.py
    └── healthcare_privacy_guard_agent.py
```

---

## ✅ Status

### MVP (Must-Have)
- ✅ Shared Components (3)
- ✅ Gastronomie-Paket Agents (6)
- ✅ Praxis-Paket Agents (6)
- ✅ Workflow-Dokumentation
- ✅ Paket-Konfiguration

### V2 (Add-ons)
- ⏳ Gastronomie V2 Agents (3)
- ⏳ Praxis V2 Agents (3)

---

## 🔒 Compliance & Sicherheit

### Gastronomie
- Allergeninformation (EU-Verordnung 1169/2011)
- Datenschutz (DSGVO)
- Payment-Sicherheit

### Praxis
- **DSGVO Art. 9** (Gesundheitsdaten = special category)
- **Schweigepflicht** (§203 StGB)
- **Berufsrechtliche Anforderungen**
- **Minimale Datenerhebung**
- **Consent-Management**
- **Retention-Policies**

---

## 🤝 Integration

### Gastronomie
- Reservierungssysteme: OpenTable, SevenRooms, Resy
- POS-Systeme: Toast, Square, Lightspeed
- Review-Plattformen: Google, Yelp, TripAdvisor

### Praxis
- PVS: Medatixx, CompuGroup, etc.
- Terminbuchung: Doctolib, Zocdoc
- E-Akte: Verschiedene Systeme

### Shared
- CRM: Salesforce, HubSpot
- Communications: Twilio, Vonage
- Knowledge Base: Verschiedene Systeme

---

## 📝 Nächste Schritte

1. **Testing**: Agents isoliert testen
2. **Integration**: Mit bestehenden Agents integrieren
3. **Global Orchestrator**: Routing-Logik erweitern
4. **Monitoring**: Observability für neue Agents
5. **V2 Agents**: Add-ons implementieren

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2024
