# Authentication Quick Start Guide

## Schnellstart-Anleitung für OAuth-Integration

### Schritt 1: Google OAuth Credentials holen

1. **Google Cloud Console öffnen**
   - Gehen Sie zu: https://console.cloud.google.com/
   - Erstellen Sie ein neues Projekt oder wählen Sie ein bestehendes

2. **OAuth Client ID erstellen**
   - Navigieren Sie zu: **APIs & Services** → **Credentials**
   - Klicken Sie auf **"Create Credentials"** → **"OAuth client ID"**
   - Falls noch nicht geschehen, konfigurieren Sie den OAuth Consent Screen
   - Wählen Sie **"Web application"** als Application type
   - **Authorized redirect URIs** hinzufügen:
     ```
     http://localhost:3000/auth/callback/google
     ```
   - Klicken Sie auf **"Create"**
   - **WICHTIG**: Kopieren Sie sofort die **Client ID** und **Client Secret** (Secret wird nur einmal angezeigt!)

3. **ENV-Variablen setzen**
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback/google
   ```

---

### Schritt 2: Microsoft OAuth Credentials holen

1. **Azure Portal öffnen**
   - Gehen Sie zu: https://portal.azure.com/
   - Melden Sie sich mit Ihrem Microsoft-Konto an

2. **App Registration erstellen**
   - Navigieren Sie zu: **Azure Active Directory** → **App registrations**
   - Klicken Sie auf **"New registration"**
   - **Name**: Ihre App (z.B. "AI Shield")
   - **Supported account types**: 
     - Wählen Sie: **"Accounts in any organizational directory and personal Microsoft accounts"**
   - **Redirect URI**:
     - Platform: **Web**
     - URI: `http://localhost:3000/auth/callback/microsoft`
   - Klicken Sie auf **"Register"**

3. **Client Secret erstellen**
   - Nach der Erstellung: Gehen Sie zu **"Certificates & secrets"**
   - Klicken Sie auf **"New client secret"**
   - **Description**: "Web App Secret"
   - **Expires**: 24 months (oder wie gewünscht)
   - Klicken Sie auf **"Add"**
   - **WICHTIG**: Kopieren Sie sofort den **Value** (wird nur einmal angezeigt!)

4. **API Permissions konfigurieren**
   - Gehen Sie zu **"API permissions"**
   - Klicken Sie auf **"Add a permission"**
   - Wählen Sie **"Microsoft Graph"**
   - Wählen Sie **"Delegated permissions"**
   - Fügen Sie hinzu:
     - `openid`
     - `email`
     - `profile`
   - Klicken Sie auf **"Add permissions"**
   - **Optional**: Klicken Sie auf **"Grant admin consent"** (für alle Benutzer)

5. **Application (client) ID kopieren**
   - Gehen Sie zu **"Overview"**
   - Kopieren Sie die **Application (client) ID**

6. **ENV-Variablen setzen**
   ```bash
   MICROSOFT_CLIENT_ID=your-application-client-id
   MICROSOFT_CLIENT_SECRET=your-client-secret-value
   MICROSOFT_REDIRECT_URI=http://localhost:3000/auth/callback/microsoft
   ```

---

### Schritt 3: Apple Sign In Credentials (Optional)

1. **Apple Developer Account**
   - Gehen Sie zu: https://developer.apple.com/
   - Melden Sie sich an (erfordert Apple Developer Program Mitgliedschaft - $99/Jahr)

2. **App ID erstellen**
   - Navigieren Sie zu: **Certificates, Identifiers & Profiles**
   - Klicken Sie auf **"Identifiers"** → **"+"**
   - Wählen Sie **"App IDs"** → **"Continue"**
   - **Description**: Ihre App
   - **Bundle ID**: z.B. `com.yourcompany.yourapp`
   - Aktivieren Sie **"Sign In with Apple"**
   - Klicken Sie auf **"Continue"** → **"Register"**

3. **Service ID erstellen**
   - Klicken Sie auf **"Identifiers"** → **"+"**
   - Wählen Sie **"Services IDs"** → **"Continue"**
   - **Description**: Ihre App Web Service
   - **Identifier**: z.B. `com.yourcompany.yourapp.web`
   - Aktivieren Sie **"Sign In with Apple"**
   - Klicken Sie auf **"Configure"**
   - **Primary App ID**: Wählen Sie Ihre App ID
   - **Website URLs**:
     - Domains: `localhost:3000`
     - Return URLs: `http://localhost:3000/auth/callback/apple`
   - Klicken Sie auf **"Save"** → **"Continue"** → **"Register"**

4. **Key erstellen**
   - Klicken Sie auf **"Keys"** → **"+"**
   - **Key Name**: "Sign In with Apple Key"
   - Aktivieren Sie **"Sign In with Apple"**
   - Klicken Sie auf **"Configure"**
   - Wählen Sie Ihre **Primary App ID**
   - Klicken Sie auf **"Save"** → **"Continue"** → **"Register"**
   - **WICHTIG**: Laden Sie die `.p8` Key-Datei herunter (nur einmal verfügbar!)
   - Notieren Sie die **Key ID**

5. **Team ID finden**
   - Gehen Sie zu: **Membership**
   - Kopieren Sie die **Team ID**

6. **ENV-Variablen setzen**
   ```bash
   APPLE_CLIENT_ID=com.yourcompany.yourapp.web
   APPLE_TEAM_ID=ABC123DEF4
   APPLE_KEY_ID=XYZ789ABC1
   APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...\n-----END PRIVATE KEY-----"
   APPLE_REDIRECT_URI=http://localhost:3000/auth/callback/apple
   ```
   
   **Hinweis**: Für `APPLE_PRIVATE_KEY` müssen Sie den Inhalt der `.p8` Datei verwenden und `\n` für Zeilenumbrüche einfügen.

---

### Schritt 4: ENV-Variablen in .env setzen

Öffnen Sie die `.env` Datei im Backend-Verzeichnis (`/Users/simple-gpt/ai-shield/.env`) und fügen Sie alle OAuth-Credentials hinzu:

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback/google

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:3000/auth/callback/microsoft

# Apple Sign In (Optional)
APPLE_CLIENT_ID=com.yourcompany.yourapp.web
APPLE_TEAM_ID=your-team-id
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
APPLE_REDIRECT_URI=http://localhost:3000/auth/callback/apple

# JWT Secret (wird automatisch generiert, wenn nicht gesetzt)
JWT_SECRET=your-secret-key-minimum-32-characters-long
```

---

### Schritt 5: Backend neu starten

```bash
cd /Users/simple-gpt/ai-shield

# Falls Docker verwendet wird:
docker compose restart control-plane

# Oder falls direkt:
cd apps/control-plane
pip install -r requirements.txt  # PyJWT installieren falls noch nicht geschehen
uvicorn app.main:app --reload --port 4051
```

---

### Schritt 6: Frontend neu starten

```bash
cd /Users/simple-gpt/frontend

# Frontend ENV-Variable setzen (falls noch nicht geschehen)
echo "NEXT_PUBLIC_CONTROL_PLANE_URL=http://localhost:4051" > .env.local

# Frontend starten
pnpm dev
# oder
npm run dev
```

---

### Schritt 7: Testen

1. Öffnen Sie: `http://localhost:3000/auth/login`

2. **Email/Password testen:**
   - Klicken Sie auf "Jetzt registrieren"
   - Geben Sie Email, Name und Passwort ein
   - Klicken Sie auf "Konto erstellen"
   - Sie sollten automatisch eingeloggt werden

3. **Google OAuth testen:**
   - Klicken Sie auf "Mit Google anmelden"
   - Sie werden zu Google weitergeleitet
   - Wählen Sie Ihr Google-Konto
   - Nach der Autorisierung werden Sie zurückgeleitet und eingeloggt

4. **Microsoft OAuth testen:**
   - Klicken Sie auf "Mit Microsoft anmelden"
   - Sie werden zu Microsoft weitergeleitet
   - Melden Sie sich mit Ihrem Microsoft-Konto an
   - Nach der Autorisierung werden Sie zurückgeleitet und eingeloggt

5. **Apple Sign In testen (falls konfiguriert):**
   - Klicken Sie auf "Mit Apple anmelden"
   - Sie werden zu Apple weitergeleitet
   - Melden Sie sich mit Ihrer Apple ID an
   - Nach der Autorisierung werden Sie zurückgeleitet und eingeloggt

---

## Troubleshooting

### Google OAuth Fehler
- **"redirect_uri_mismatch"**: Stellen Sie sicher, dass die Redirect URI in Google Cloud Console exakt übereinstimmt
- **"invalid_client"**: Überprüfen Sie Client ID und Secret

### Microsoft OAuth Fehler
- **"AADSTS50011"**: Redirect URI stimmt nicht überein - überprüfen Sie die App Registration
- **"invalid_client"**: Überprüfen Sie Client ID und Secret
- **"AADSTS7000215"**: Client Secret ist abgelaufen - erstellen Sie einen neuen Secret

### Apple Sign In Fehler
- **"invalid_client_id"**: Überprüfen Sie die Service ID
- **"invalid_request"**: Überprüfen Sie die Redirect URI und Domain-Konfiguration

### Allgemeine Fehler
- **Backend nicht erreichbar**: Stellen Sie sicher, dass der Backend-Server auf Port 4051 läuft
- **CORS-Fehler**: Überprüfen Sie die CORS-Konfiguration in `main.py`
- **Token-Fehler**: Überprüfen Sie die JWT_SECRET Variable

---

## Nächste Schritte nach erfolgreichem Setup

1. ✅ OAuth-Integration funktioniert
2. ⏳ User-Datenbank migrieren (von in-memory zu PostgreSQL)
3. ⏳ Passwort-Hashing auf bcrypt/argon2 umstellen
4. ⏳ Email-Verifizierung implementieren
5. ⏳ Passwort-Reset-Funktion hinzufügen
6. ⏳ 2FA (Two-Factor Authentication) hinzufügen

---

## Support

Bei Problemen:
1. Überprüfen Sie die Browser-Konsole auf Fehler
2. Überprüfen Sie die Backend-Logs
3. Überprüfen Sie die ENV-Variablen
4. Siehe `AUTH_SETUP.md` für detaillierte Dokumentation
