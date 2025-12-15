# Workflow-Dokumentation für Branchen-Pakete

Diese Dokumentation beschreibt die konkreten Workflows für beide Branchen-Pakete.

---

## Gastronomie-Paket - Workflows

### Workflow G1: Telefon → Reservierung (24/7)

**Ziel:** 24/7 Reservierungsannahme ohne verpasste Anrufe

**Ablauf:**
1. `telephonyRealtime.ts` nimmt Call an → `communications_supervisor`
2. `global_orchestrator_agent` erkennt "Gastro-Account" (via `vertical_package_manifest`) → `gastronomy_supervisor_agent`
3. `gastronomy_supervisor_agent` erkennt Intent "RESERVATION" → `restaurant_voice_host_agent`
4. `restaurant_voice_host_agent` führt Dialog:
   - Datum/Uhrzeit/Personen/Name/Telefon abfragen
   - Verfügbarkeit prüfen via `check_availability()`
5. `integration_agent` bucht in Reservierungssystem (z.B. OpenTable/SevenRooms/...)
6. Bestätigung per SMS/E-Mail über `communications_supervisor`
7. Logging:
   - `crm_contact_agent` / `crm_create_note`
   - Optional: `memory_write` (Buchungsregeln lernen)

**Technische Details:**
- Integration: Standard-Reservierungssysteme (OpenTable, SevenRooms, etc.)
- Bestätigung: Automatisch via Communications Supervisor
- Fallback: Bei Komplexität → `handoff_to_human_protocol`

---

### Workflow G2: Telefon/Chat → "Allergene / vegan / glutenfrei"

**Ziel:** Rechtssichere Allergen-Auskünfte

**Ablauf:**
1. Anfrage → `restaurant_voice_host_agent`
2. Routing → `restaurant_menu_allergen_agent`
3. Quellen:
   - Menü-PDF (via `document_intelligence_agent`)
   - Allergenmatrix in Memory (via `knowledge_base_agent`)
4. Antwort inkl. "Spuren möglich / bitte Personal informieren" (Guardrails)
5. Optional: "Allergen-Report" fürs Team (was wird am häufigsten gefragt)

**Technische Details:**
- Guardrails: Strikte Wording-Regeln (keine Garantien, immer "bitte Personal informieren")
- Datenquelle: Menü + Rezeptbuch/Allergenmatrix
- Compliance: EU-Verordnung 1169/2011 (Allergenkennzeichnung)

---

### Workflow G3: Telefon/SMS → Takeout Bestellung

**Ziel:** Takeout-Bestellungen ohne Personal-Belastung

**Ablauf:**
1. Anfrage → `restaurant_takeout_order_agent`
2. Agent validiert Menüvarianten, fragt Rückfragen, upsellt
3. `integration_agent` → POS/KDS oder zumindest "Kitchen Ticket" erstellen
4. Zahlungs-/Abholinfo via `communications_supervisor`

**Technische Details:**
- Integration: POS-Systeme (Toast, Square, etc.) oder Kitchen Display System
- Payment: "pay at pickup" oder Payment-Link
- Upselling: Basierend auf bereits bestellten Items

---

### Workflow G4: Web-Widget → "Heute noch Tisch frei?"

**Ziel:** Reservierungen direkt von Website

**Ablauf:**
1. `website_workflow_agent` → `gastronomy_supervisor_agent`
2. `gastronomy_supervisor_agent` → `restaurant_voice_host_agent`
3. Gleiche Booking-Logik wie am Telefon, nur Chat

**Technische Details:**
- Channel: Website-Widget (Chat)
- Gleiche Logik wie Workflow G1

---

### Workflow G5: Event/Catering Anfrage → Angebot in 15 Minuten

**Ziel:** Gruppenbuchungen automatisiert abwickeln

**Ablauf:**
1. `restaurant_events_catering_agent` sammelt Eckdaten:
   - Datum, Gästezahl, Event-Type, Budget
2. `crm_deal_agent` legt Deal an
3. `proposal_agent` erstellt Angebot
4. `followup_agent` startet Sequence
5. `personalization_agent` passt Ton/Details an (Firmenname, Anlass)

**Technische Details:**
- CRM-Integration: Automatische Deal-Erstellung
- Proposal: Template-basiert, personalisiert
- Follow-up: Automatische Sequenz

---

### Workflow G6: Review rein → Antwortvorschlag + Eskalation

**Ziel:** Reputation-Management automatisiert

**Ablauf:**
1. Trigger (Google/Yelp) → `restaurant_reputation_agent`
2. Triage: "kritisch/neutral/positiv"
3. `marketing_execution_agent` formuliert Antwort
4. Optional: Human approval in UI, dann posten

**Technische Details:**
- Integration: Review-APIs (Google, Yelp, TripAdvisor)
- Sentiment-Analyse: NLP-basiert
- Eskalation: Bei kritischen Reviews

---

## Praxis-Paket - Workflows

### Workflow P1: Telefon → Termin buchen/verschieben/stornieren

**Ziel:** Terminbuchung ohne Warteschleife

**Ablauf:**
1. Call → `communications_supervisor`
2. `global_orchestrator_agent` → `practice_supervisor_agent`
3. `practice_phone_reception_agent` fragt minimal nötige Infos ab (Datensparsamkeit!)
4. `integration_agent` schreibt/liest Termin im System (Doctolib/PVS/Calendar)
5. Bestätigung + ggf. Vorbereitungsinfos über `communications_supervisor`

**Technische Details:**
- Integration: PVS (Praxisverwaltungssystem), Doctolib, Calendar
- Datensparsamkeit: Nur Name, Telefon, Datum, Zeit
- Compliance: DSGVO Art. 9 (Gesundheitsdaten)

---

### Workflow P2: Reminder Journey → Bestätigung/Absage → Warteliste

**Ziel:** No-Show-Reduktion durch Erinnerungen

**Ablauf:**
1. Trigger (neuer Termin/Reminder) → `practice_appointment_reminder_agent`
2. Patient antwortet: "JA/NEIN/verschieben" → Agent aktualisiert Termin + Warteliste
3. Journey-Pattern orientiert sich an NexHealth-Triggern:
   - Confirmed
   - Reminders (1 Tag vorher, 1 Stunde vorher)
   - Missed
   - Cancelled
   - Recalls

**Technische Details:**
- Channel: SMS/E-Mail
- Automatische Warteliste-Verwaltung
- Recall-Strategie bei No-Shows

---

### Workflow P3: Pre-Visit Intake → Formulare & Einverständnis

**Ziel:** Digitale Formulare vor dem Termin

**Ablauf:**
1. `practice_patient_intake_forms_agent` sendet Form-Link + Erinnerung
2. Dokumente rein → `document_intelligence_agent` strukturiert
3. `integration_agent` → Ablage in PVS/E-Akte

**Technische Details:**
- Formulare: Anamnese, Einverständnis, Versicherung, Datenschutz
- Integration: PVS/E-Akte
- Erinnerung: Automatisch bei ausstehenden Formularen

---

### Workflow P4: Rezept/Überweisung/AU → "Aufnehmen → intern Task → Rückmeldung"

**Ziel:** Routine-Anliegen automatisiert abwickeln

**Ablauf:**
1. `practice_admin_requests_agent` nimmt Anliegen auf
2. Erzeugt Task für Team (Backoffice/Inbox) + Status-Updates an Patient
3. Kein medizinischer Inhalt, nur Prozess (sicher + skalierbar)

**Technische Details:**
- Request-Types: Rezept, Überweisung, AU, Befundkopie
- Task-System: Internes Backoffice
- Status-Updates: Automatisch an Patient

---

### Workflow P5: "Ich habe Symptome …" → Safety Routing (ohne Diagnose)

**Ziel:** Sicherer Umgang mit medizinischen Inhalten

**Ablauf:**
1. `practice_supervisor_agent` erkennt medizinischen Inhalt
2. `healthcare_privacy_guard_agent` schaltet auf sicheren Modus:
   - Bei Alarmzeichen: "112/Notaufnahme" (standardisiert)
   - Sonst: Termin anbieten / Rückruf anfordern

**Technische Details:**
- Safety-Check: Automatisch bei Symptom-Keywords
- Keine Diagnose: Nur Standardantworten
- Compliance: DSGVO Art. 9 + Schweigepflicht

---

### Workflow P6: (Optional) Arzt-Doku nach Gespräch

**Ziel:** Dokumentations-Entwürfe für Behandler

**Ablauf:**
1. `summarizer_agent` / `practice_clinical_documentation_agent` erstellt Doku-Entwurf
2. Arzt prüft/editiert → `integration_agent` schreibt in EHR/PVS

**Technische Details:**
- Nur für Behandler, nicht für Patienten
- Human Review erforderlich
- Integration: EHR/PVS

---

## Shared Workflows

### Workflow S1: Consent & Redaction Pipeline

**Ziel:** PII/PHI-Schutz vor Memory/Logs

**Ablauf:**
1. Request kommt rein
2. `consent_and_redaction_gateway` prüft Consent
3. Content wird redactiert (PII/PHI entfernt)
4. Retention-Policy wird angewendet
5. Weiterleitung an Agents

**Technische Details:**
- Pipeline-Komponente: Vor Memory/Logs geschaltet
- Compliance: DSGVO Art. 9 (Gesundheitsdaten)
- Redaction: Automatisch basierend auf Regeln

---

### Workflow S2: Human Handoff Protocol

**Ziel:** Einheitliche Eskalation

**Ablauf:**
1. Agent erkennt Handoff-Bedarf
2. `handoff_to_human_protocol` entscheidet Methode:
   - LIVE_TRANSFER (Telefon)
   - TICKET (Backoffice)
   - CALLBACK (Rückruf)
3. Handoff-Context wird erstellt
4. Team wird informiert

**Technische Details:**
- Priorität: Automatisch basierend auf Reason
- Method: Abhängig von Channel und Reason
- Tracking: Alle Handoffs werden geloggt

---

## Integration Points

### Gastronomie
- Reservierungssysteme: OpenTable, SevenRooms, Resy
- POS-Systeme: Toast, Square, Lightspeed
- Review-Plattformen: Google, Yelp, TripAdvisor

### Praxis
- PVS: Verschiedene Systeme (z.B. Medatixx, CompuGroup)
- Terminbuchung: Doctolib, Zocdoc
- E-Akte: Verschiedene Systeme

### Shared
- CRM: Salesforce, HubSpot, etc.
- Communications: Twilio, Vonage, etc.
- Knowledge Base: Verschiedene Systeme
