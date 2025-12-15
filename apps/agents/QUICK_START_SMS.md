# Quick Start: SMS senden

## Schritt 1: Backend-Service starten

```bash
cd apps/communications-service
pip install -r requirements.txt

# .env erstellen mit Twilio Credentials
echo "TWILIO_ACCOUNT_SID=your_account_sid" > .env
echo "TWILIO_AUTH_TOKEN=your_auth_token" >> .env
echo "TWILIO_PHONE_NUMBER=+1234567890" >> .env

# Service starten
uvicorn main:app --port 8001
```

## Schritt 2: Agent-System konfigurieren

```bash
# In .env des Agent-Systems
COMMUNICATIONS_API_URL=http://localhost:8001/api/v1/communications
COMMUNICATIONS_API_KEY=your_api_key  # Optional
```

## Schritt 3: SMS senden (Python)

```python
from apps.agents.core.real_integrations import get_communications_supervisor
import asyncio

async def send_sms():
    comm = get_communications_supervisor()
    result = await comm.send_sms(
        phone_number="+49123456789",
        message="Hallo! Das ist eine Test-SMS.",
        account_id="123"
    )
    print(f"Success: {result.success}")
    print(f"Message ID: {result.message_id}")

# Ausführen
asyncio.run(send_sms())
```

## Schritt 4: SMS senden (in Agent)

```python
# In einem Agent (z.B. restaurant_voice_host_agent.py)
from apps.agents.core.real_integrations import get_communications_supervisor

class RestaurantVoiceHostAgent:
    async def send_confirmation_sms(self, phone_number: str, message: str):
        comm = get_communications_supervisor()
        result = await comm.send_sms(
            phone_number=phone_number,
            message=message,
            account_id=self.account_id
        )
        return result.success
```

## Was passiert?

1. **Agent ruft `comm.send_sms()` auf**
2. **CommunicationsSupervisor sendet HTTP-Request** zu Backend-Service
3. **Backend-Service sendet SMS** via Twilio
4. **Twilio sendet SMS** an Empfänger
5. **Response kommt zurück** mit Message ID

## Troubleshooting

### "Twilio credentials nicht konfiguriert"
→ Prüfe `.env` im Communications-Service

### "Connection refused"
→ Backend-Service läuft nicht auf Port 8001

### "Unauthorized"
→ API Key stimmt nicht überein

## Nächste Schritte

- ✅ SMS funktioniert
- ⚠️ Email: SendGrid konfigurieren
- ⚠️ Phone: Twilio Voice implementieren
- ⚠️ Chat: WebSocket-Integration
