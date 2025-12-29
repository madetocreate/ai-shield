# Authentication Environment Variables Template

## Backend (.env)

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback/google

# Microsoft OAuth Configuration
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:3000/auth/callback/microsoft

# Apple Sign In Configuration
APPLE_CLIENT_ID=com.yourcompany.yourapp
APPLE_TEAM_ID=ABC123DEF4
APPLE_KEY_ID=XYZ789ABC1
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...\n-----END PRIVATE KEY-----"
APPLE_REDIRECT_URI=http://localhost:3000/auth/callback/apple

# JWT Configuration
JWT_SECRET=your-secret-key-minimum-32-characters-long
# JWT_EXPIRATION_HOURS=168  # Optional: Default is 7 days (168 hours)
```

## Frontend (.env.local)

```bash
NEXT_PUBLIC_CONTROL_PLANE_URL=http://localhost:4051
```

## Setup Instructions

### 1. Google OAuth Setup

1. Gehen Sie zu: https://console.cloud.google.com/
2. Erstellen Sie ein Projekt oder wählen Sie ein bestehendes
3. APIs & Services → Credentials
4. Create Credentials → OAuth client ID
5. Application type: Web application
6. Authorized redirect URIs: `http://localhost:3000/auth/callback/google`
7. Kopieren Sie Client ID und Client Secret

### 2. Microsoft OAuth Setup

1. Gehen Sie zu: https://portal.azure.com/
2. Azure Active Directory → App registrations
3. New registration
4. Name: Ihre App
5. Supported account types: Accounts in any organizational directory and personal Microsoft accounts
6. Redirect URI: `http://localhost:3000/auth/callback/microsoft` (Web)
7. Nach Erstellung: Application (client) ID kopieren
8. Certificates & secrets → New client secret → Kopieren Sie den Secret
9. API permissions: Microsoft Graph → Delegated permissions → `openid`, `email`, `profile`

### 3. Apple Sign In Setup

1. Gehen Sie zu: https://developer.apple.com/
2. Certificates, Identifiers & Profiles
3. Erstellen Sie eine App ID mit "Sign In with Apple"
4. Erstellen Sie eine Service ID für Web
5. Erstellen Sie einen Key für "Sign In with Apple"
6. Laden Sie die `.p8` Datei herunter
7. Notieren Sie Key ID und Team ID

### 4. ENV-Variablen setzen

```bash
# Backend
cd /Users/simple-gpt/ai-shield
# Fügen Sie die Variablen zu .env hinzu

# Frontend
cd /Users/simple-gpt/frontend
# Erstellen Sie .env.local mit NEXT_PUBLIC_CONTROL_PLANE_URL
```

## Production

Für Production ändern Sie:
- `GOOGLE_OAUTH_REDIRECT_URI` → Ihre Production-URL
- `APPLE_REDIRECT_URI` → Ihre Production-URL
- `JWT_SECRET` → Starker, zufälliger Secret (mindestens 32 Zeichen)
- Verwenden Sie eine Datenbank statt in-memory Storage
- Verwenden Sie bcrypt/argon2 für Passwort-Hashing
