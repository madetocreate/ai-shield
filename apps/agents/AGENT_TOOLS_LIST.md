# Agent Tools List - Alle Agents als MCP Tools

## 📋 Übersicht

Alle Agents sind als MCP Tools registriert und mit ihren Supervisors verbunden.

## 🍽️ Gastronomie-Paket (9 Agents)

### Supervisor
- **gastronomy_supervisor_agent** (Supervisor)
  - Routet Gastro-Anfragen intelligent

### MVP Agents (6)
1. **restaurant_voice_host_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Reservierungen, Öffnungszeiten, Adresse, allgemeine Infos
   - MCP Tool: `agent_restaurant_voice_host_agent`

2. **restaurant_takeout_order_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Takeout Bestellungen, Upselling, POS-Integration
   - MCP Tool: `agent_restaurant_takeout_order_agent`

3. **restaurant_menu_allergen_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Allergen-Auskünfte, Diäten, rechtssichere Auskünfte
   - MCP Tool: `agent_restaurant_menu_allergen_agent`

4. **restaurant_events_catering_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Events & Catering, Gruppenbuchungen, Angebote
   - MCP Tool: `agent_restaurant_events_catering_agent`

5. **restaurant_reputation_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Review-Management, Antworten generieren
   - MCP Tool: `agent_restaurant_reputation_agent`

6. **restaurant_events_catering_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Events & Catering
   - MCP Tool: `agent_restaurant_events_catering_agent`

### V2 Agents (3)
7. **restaurant_shift_staffing_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Schichtplanung, Ausfälle, Ersatz
   - MCP Tool: `agent_restaurant_shift_staffing_agent`

8. **restaurant_inventory_procurement_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Bestandsverwaltung, Nachbestellung
   - MCP Tool: `agent_restaurant_inventory_procurement_agent`

9. **restaurant_daily_ops_report_agent**
   - Supervisor: `gastronomy_supervisor_agent`
   - Beschreibung: Tagesabschlussberichte
   - MCP Tool: `agent_restaurant_daily_ops_report_agent`

---

## 🏥 Praxis-Paket (9 Agents)

### Supervisor
- **practice_supervisor_agent** (Supervisor)
  - Routet Praxis-Anfragen mit Safety-Check

### MVP Agents (6)
1. **practice_phone_reception_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Termine, Öffnungszeiten, Safety-Routing
   - MCP Tool: `agent_practice_phone_reception_agent`

2. **practice_appointment_reminder_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Terminerinnerungen, No-Show-Reduktion
   - MCP Tool: `agent_practice_appointment_reminder_agent`

3. **practice_patient_intake_forms_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Digitale Formulare, Anamnese
   - MCP Tool: `agent_practice_patient_intake_forms_agent`

4. **practice_admin_requests_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Rezepte, Überweisungen, AU
   - MCP Tool: `agent_practice_admin_requests_agent`

5. **healthcare_privacy_guard_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: DSGVO-Compliance, Schweigepflicht
   - MCP Tool: `agent_healthcare_privacy_guard_agent`

6. **practice_supervisor_agent**
   - Supervisor: None (ist selbst Supervisor)
   - Beschreibung: Praxis Supervisor
   - MCP Tool: `agent_practice_supervisor_agent`

### V2 Agents (3)
7. **practice_clinical_documentation_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Klinische Dokumentation für Behandler
   - MCP Tool: `agent_practice_clinical_documentation_agent`

8. **practice_billing_insurance_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Rechnungsfragen, Versicherung
   - MCP Tool: `agent_practice_billing_insurance_agent`

9. **practice_document_inbox_agent**
   - Supervisor: `practice_supervisor_agent`
   - Beschreibung: Dokumentenverwaltung
   - MCP Tool: `agent_practice_document_inbox_agent`

---

## 🔧 Allgemeine Agents (2)

### Supervisor
- **support_triage_agent** (Supervisor)
  - Routet Support-Anfragen

### Agents
1. **support_triage_agent**
   - Supervisor: None (ist selbst Supervisor)
   - Beschreibung: Support Triage
   - MCP Tool: `agent_support_triage_agent`

2. **support_resolution_agent**
   - Supervisor: `support_triage_agent`
   - Beschreibung: Support Resolution
   - MCP Tool: `agent_support_resolution_agent`

---

## 📊 Zusammenfassung

| Package | Agents | Supervisors | Total Tools |
|---------|--------|-------------|-------------|
| Gastronomie | 9 | 1 | 9 |
| Praxis | 9 | 1 | 9 |
| Allgemein | 2 | 1 | 2 |
| **Total** | **20** | **3** | **20** |

---

## ✅ Verifikation

```bash
python apps/agents/scripts/verify_supervisor_connections.py
```

**Erwartetes Ergebnis:**
- ✅ Alle 20 Agents registriert
- ✅ Alle Supervisor-Verbindungen korrekt
- ✅ Alle als MCP Tools verfügbar

---

**Version:** 1.0.0
