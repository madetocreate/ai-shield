# Integration Setup Guide - Was ist fertig, was fehlt?

## ✅ Was ist bereits fertig

### Client-Seite (Agent-System)
- ✅ **CommunicationsSupervisor Klasse** - Bereit, SMS/Email/Phone zu senden
- ✅ **IntegrationAgent Klasse** - Bereit, Reservierungen/Termine zu erstellen
- ✅ **KnowledgeBaseAgent Klasse** - Bereit, in Knowledge Base zu suchen
- ✅ **CRMAgent Klasse** - Bereit, CRM-Operationen durchzuführen

**Das bedeutet:** Die Agent-Seite ist fertig und kann mit Backend-Services kommunizieren.

---

## ❌ Was noch fehlt

### Backend-Services (API-Endpoints)

Die Integrationen erwarten Backend-Services, die noch **nicht existieren**:

1. **Communications API** (`/api/v1/communications/send`)
   - Erwartet: `POST http://localhost:8000/api/v1/communications/send`
   - Sendet: SMS, Email, Phone, Chat
   - **Status:** ❌ Nicht vorhanden

2. **Integration API** (`/api/v1/integrations/execute`)
   - Erwartet: `POST http://localhost:8000/api/v1/integrations/execute`
   - Führt aus: Reservierungen, Termine, etc.
   - **Status:** ❌ Nicht vorhanden

3. **Knowledge Base API** (`/api/v1/knowledge/search`)
   - Erwartet: `POST http://localhost:8000/api/v1/knowledge/search`
   - Sucht: In Knowledge Base
   - **Status:** ❌ Nicht vorhanden

4. **CRM API** (`/api/v1/crm/contacts`, `/api/v1/crm/deals`, etc.)
   - Erwartet: `POST http://localhost:8000/api/v1/crm/...`
   - Erstellt: Kontakte, Deals, Notizen
   - **Status:** ❌ Nicht vorhanden

---

## 🎯 Optionen: Wie weiter?

### Option A: Backend-Service erstellen (Empfohlen)

Erstelle einen einfachen Backend-Service, der die API-Endpoints bereitstellt und mit echten Services (Twilio, SendGrid, etc.) kommuniziert.

**Vorteile:**
- ✅ Vollständige Kontrolle
- ✅ Einheitliche API
- ✅ Einfache Erweiterung

**Nachteile:**
- ⚠️ Muss selbst gebaut werden

---

### Option B: Direkte Integration mit echten Services

Integriere direkt mit echten Services (Twilio für SMS, SendGrid für Email, etc.).

**Vorteile:**
- ✅ Schnell einsatzbereit
- ✅ Kein Backend-Service nötig

**Nachteile:**
- ⚠️ Mehrere Services zu verwalten
- ⚠️ Unterschiedliche APIs

---

### Option C: Bestehenden Service nutzen

Falls du bereits einen Communications-Service hast, verbinde die Integrationen damit.

**Vorteile:**
- ✅ Nutzt bestehende Infrastruktur

**Nachteile:**
- ⚠️ Muss an bestehende API angepasst werden

---

## 🚀 Empfehlung: Option A + B (Hybrid)

**Kombiniere beide Ansätze:**

1. **Backend-Service erstellen** für einheitliche API
2. **Echte Services integrieren** (Twilio, SendGrid, etc.) im Backend

**So funktioniert es:**
```
Agent System → Backend-Service → Twilio/SendGrid/etc.
```

---

## 📝 Konkrete Schritte für SMS

### Schritt 1: Backend-Service erstellen

Erstelle einen FastAPI-Service, der die Communications-API bereitstellt:

```python
# apps/communications-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()

class SendMessageRequest(BaseModel):
    channel: str
    recipient: str
    message: str
    account_id: str
    user_id: Optional[str] = None

@app.post("/api/v1/communications/send")
async def send_message(request: SendMessageRequest):
    if request.channel == "sms":
        # Twilio Integration
        result = await send_sms_via_twilio(
            to=request.recipient,
            message=request.message
        )
        return {"success": True, "message_id": result.sid}
    elif request.channel == "email":
        # SendGrid Integration
        result = await send_email_via_sendgrid(
            to=request.recipient,
            message=request.message
        )
        return {"success": True, "message_id": result.id}
    # ...
```

### Schritt 2: Twilio konfigurieren

```bash
# .env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Schritt 3: Agent-System konfigurieren

```bash
# .env
COMMUNICATIONS_API_URL=http://localhost:8001/api/v1/communications
COMMUNICATIONS_API_KEY=your_api_key
```

### Schritt 4: SMS senden

```python
from apps.agents.core.real_integrations import get_communications_supervisor

comm = get_communications_supervisor()
result = await comm.send_sms(
    phone_number="+49123456789",
    message="Hallo!",
    account_id="123"
)
```

---

## 🔧 Was muss konfiguriert werden?

### 1. Backend-Service starten
```bash
# Communications Service
cd apps/communications-service
uvicorn main:app --port 8001
```

### 2. ENV-Variablen setzen
```bash
# Agent-System
COMMUNICATIONS_API_URL=http://localhost:8001/api/v1/communications
COMMUNICATIONS_API_KEY=your_api_key

# Backend-Service
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
SENDGRID_API_KEY=your_sendgrid_key
```

### 3. Services verbinden
- Backend-Service läuft auf Port 8001
- Agent-System konfiguriert auf Backend-Service
- Backend-Service kommuniziert mit Twilio/SendGrid/etc.

---

## 📊 Aktueller Status

| Komponente | Status | Was fehlt |
|------------|--------|-----------|
| **Agent-System (Client)** | ✅ Fertig | Nichts |
| **Backend-Service** | ❌ Fehlt | Muss erstellt werden |
| **Twilio/SendGrid/etc.** | ❌ Fehlt | Muss konfiguriert werden |

---

## 💡 Nächste Schritte

1. **Backend-Service erstellen** (siehe Beispiel oben)
2. **Twilio/SendGrid Accounts erstellen** und API-Keys holen
3. **Backend-Service mit Services verbinden**
4. **Agent-System konfigurieren** (ENV-Variablen)
5. **Testen:** SMS/Email senden

---

**Zusammenfassung:** Die Agent-Seite ist fertig, aber du brauchst noch einen Backend-Service, der die API-Endpoints bereitstellt und mit echten Services (Twilio, SendGrid, etc.) kommuniziert.
