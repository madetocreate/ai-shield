# Communications Service

Backend-Service für SMS, Email, Phone, Chat.

## Setup

### 1. Installiere Dependencies

```bash
cd apps/communications-service
pip install -r requirements.txt
```

### 2. Konfiguriere ENV-Variablen

Erstelle `.env` Datei:

```bash
# Twilio (für SMS & Phone)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid (für Email)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@example.com

# API Key (optional, für Authentifizierung)
COMMUNICATIONS_API_KEY=your_api_key
```

### 3. Starte Service

```bash
uvicorn main:app --port 8001 --reload
```

Service läuft auf: `http://localhost:8001`

## API Endpoints

### POST `/api/v1/communications/send`

Sendet Nachricht über verschiedenen Channel.

**Request:**
```json
{
  "channel": "sms",
  "recipient": "+49123456789",
  "message": "Hallo!",
  "account_id": "123",
  "user_id": "456",
  "metadata": {
    "subject": "Test"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "SM123456789",
  "metadata": {
    "status": "queued"
  }
}
```

## Channels

- `sms`: SMS via Twilio
- `email`: Email via SendGrid
- `phone`: Phone Call via Twilio Voice (TODO)
- `chat`: Chat Message (Placeholder)
- `website`: Website Widget Message (Placeholder)

## Agent-System konfigurieren

In Agent-System `.env`:

```bash
COMMUNICATIONS_API_URL=http://localhost:8001/api/v1/communications
COMMUNICATIONS_API_KEY=your_api_key
```

## Testen

```bash
curl -X POST http://localhost:8001/api/v1/communications/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "channel": "sms",
    "recipient": "+49123456789",
    "message": "Test SMS",
    "account_id": "123"
  }'
```
