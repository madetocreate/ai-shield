# Changelog - Branchen-Pakete

## [1.0.0] - 2024

### ✨ Added

#### Shared Components
- `vertical_package_manifest` - Konfigurationssystem für Branchen-Pakete
- `consent_and_redaction_gateway` - PII/PHI-Schutz mit Consent-Management
- `handoff_to_human_protocol` - Einheitlicher Eskalationsstandard

#### Core Components
- `agent_registry` - Zentrale Agent-Registrierung mit Dependency Injection
- `global_orchestrator_agent` - Zentrale Routing-Logik

#### Gastronomie-Paket (MVP)
- `gastronomy_supervisor_agent` - Vertical Router
- `restaurant_voice_host_agent` - Telefon/Chat-Host
- `restaurant_menu_allergen_agent` - Allergen-Auskünfte
- `restaurant_takeout_order_agent` - Takeout-Bestellungen
- `restaurant_reputation_agent` - Review-Management
- `restaurant_events_catering_agent` - Events/Catering

#### Gastronomie-Paket (V2)
- `restaurant_shift_staffing_agent` - Schichtplanung & Ausfälle
- `restaurant_inventory_procurement_agent` - Bestandsverwaltung
- `restaurant_daily_ops_report_agent` - Tagesabschlussberichte

#### Praxis-Paket (MVP)
- `practice_supervisor_agent` - Vertical Router mit Safety-Check
- `practice_phone_reception_agent` - AI-Empfang
- `practice_appointment_reminder_agent` - No-Show-Reduktion
- `practice_patient_intake_forms_agent` - Digitale Formulare
- `practice_admin_requests_agent` - Routine-Anliegen
- `healthcare_privacy_guard_agent` - DSGVO/Schweigepflicht-Guardrails

#### Praxis-Paket (V2)
- `practice_clinical_documentation_agent` - Doku-Entwürfe für Behandler
- `practice_billing_insurance_agent` - Rechnungsfragen
- `practice_document_inbox_agent` - Dokumentenverwaltung

#### Testing
- Tests für alle Gastronomie-Agents
- Tests für alle Praxis-Agents
- Tests für Shared Components
- Tests für Global Orchestrator

#### Dokumentation
- README.md - Übersicht
- WORKFLOWS.md - Workflow-Details
- PACKAGE_CONFIGURATION.md - Konfiguration
- INTEGRATION_GUIDE.md - Integration Guide
- CHANGELOG.md - Diese Datei

### 🔧 Features

- **Konfigurierbar**: Pakete per Manifest aktivierbar
- **DSGVO-konform**: Consent-Management, Redaction, Retention
- **Safety-First**: Besonders für Praxis (keine Diagnosen, Safety-Routing)
- **Skalierbar**: Shared Components für beide Pakete
- **Testbar**: Umfassende Test-Suite
- **Dokumentiert**: Vollständige Dokumentation

### 🐛 Fixed

- Import-Fehler in `restaurant_events_catering_agent`
- Import-Fehler in `healthcare_privacy_guard_agent`
- Syntax-Fehler in `practice_document_inbox_agent`

### 📝 Notes

- Alle Agents sind MVP-ready
- V2 Agents sind Add-ons und optional
- Integration mit bestehenden Agents über Dependency Injection
- Global Orchestrator routet automatisch basierend auf Package Manifest

---

## [Unreleased]

### Geplant

- Integration mit bestehenden Backend-Agents
- Performance-Optimierungen
- Erweiterte Monitoring-Integration
- CI/CD Pipeline für Tests
