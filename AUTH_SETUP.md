# Authentication Setup Guide

## Übersicht

Vollständiges Login/Signup-System mit:
- ✅ Email/Password Authentication
- ✅ Google OAuth Login
- ✅ Apple Sign In
- ✅ JWT-basierte Session-Verwaltung
- ✅ Geschützte Routen

## Backend-Endpunkte

### Email Signup
```
POST /v1/auth/signup/email
Body: { email, password, name? }
Response: { access_token, user, expires_in }
```

### Email Login
```
POST /v1/auth/login/email
Body: { email, password }
Response: { access_token, user, expires_in }
```

### Google OAuth
```
GET /v1/auth/google/authorize
Response: { auth_url }

POST /v1/auth/login/google
Body: { code, redirect_uri }
Response: { access_token, user, expires_in }
```

### Microsoft OAuth
```
GET /v1/auth/microsoft/authorize
Response: { auth_url }

POST /v1/auth/login/microsoft
Body: { code, redirect_uri }
Response: { access_token, user, expires_in }
```

### Apple Sign In
```
GET /v1/auth/apple/authorize
Response: { auth_url }

POST /v1/auth/login/apple
Body: { id_token, user? }
Response: { access_token, user, expires_in }
```

### Get Current User
```
GET /v1/auth/me
Headers: Authorization: Bearer <token>
Response: { id, email, name, picture, provider, created_at }
```

## Frontend-Routen

- `/auth/login` - Login/Signup-Seite
- `/auth/callback/google` - Google OAuth Callback
- `/auth/callback/microsoft` - Microsoft OAuth Callback
- `/auth/callback/apple` - Apple Sign In Callback

## ENV-Variablen (Backend)

Fügen Sie diese Variablen zu Ihrer `.env` Datei hinzu:

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback/google

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:3000/auth/callback/microsoft

# Apple Sign In
APPLE_CLIENT_ID=com.yourcompany.yourapp
APPLE_TEAM_ID=your-team-id
APPLE_KEY_ID=your-key-id
APPLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----
APPLE_REDIRECT_URI=http://localhost:3000/auth/callback/apple

# JWT
JWT_SECRET=your-secret-key-min-32-chars
```

## Microsoft OAuth Setup

1. **Azure Portal**
   - Gehen Sie zu: https://portal.azure.com/
   - Azure Active Directory → App registrations
   - Klicken Sie auf "New registration"
   - Name: Ihre App
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:3000/auth/callback/microsoft` (Platform: Web)
   - Klicken Sie auf "Register"
   - Kopieren Sie die "Application (client) ID"
   - Gehen Sie zu "Certificates & secrets"
   - Klicken Sie auf "New client secret"
   - Beschreibung: "Web App Secret"
   - Expires: 24 months (oder wie gewünscht)
   - Kopieren Sie den "Value" (nur einmal sichtbar!)
   - Gehen Sie zu "API permissions"
   - Klicken Sie auf "Add a permission" → Microsoft Graph → Delegated permissions
   - Fügen Sie hinzu: `openid`, `email`, `profile`
   - Klicken Sie auf "Grant admin consent"

2. **ENV-Variablen setzen**
   ```bash
   MICROSOFT_CLIENT_ID=your-application-client-id
   MICROSOFT_CLIENT_SECRET=your-client-secret-value
   MICROSOFT_REDIRECT_URI=http://localhost:3000/auth/callback/microsoft
   ```

## Google OAuth Setup

1. **Google Cloud Console**
   - Gehen Sie zu: https://console.cloud.google.com/
   - Erstellen Sie ein neues Projekt oder wählen Sie ein bestehendes
   - Gehen Sie zu: APIs & Services → Credentials
   - Klicken Sie auf "Create Credentials" → "OAuth client ID"
   - Wählen Sie "Web application"
   - Authorized redirect URIs: `http://localhost:3000/auth/callback/google`
   - Kopieren Sie Client ID und Client Secret

2. **ENV-Variablen setzen**
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   ```

## Apple Sign In Setup (Optional)

1. **Apple Developer Account**
   - Gehen Sie zu: https://developer.apple.com/
   - Erstellen Sie eine App ID mit "Sign In with Apple" aktiviert
   - Erstellen Sie eine Service ID für Web-Anwendungen
   - Erstellen Sie einen Key für "Sign In with Apple"
   - Laden Sie die `.p8` Key-Datei herunter
   - Notieren Sie Key ID und Team ID

2. **ENV-Variablen setzen**
   ```bash
   APPLE_CLIENT_ID=com.yourcompany.yourapp
   APPLE_TEAM_ID=ABC123DEF4
   APPLE_KEY_ID=XYZ789ABC1
   APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...\n-----END PRIVATE KEY-----"
   ```

## Frontend ENV-Variablen

Erstellen Sie `.env.local` im Frontend-Verzeichnis:

```bash
NEXT_PUBLIC_CONTROL_PLANE_URL=http://localhost:4051
```

## Verwendung

### Login-Seite öffnen
```
http://localhost:3000/auth/login
```

### Geschützte Routen
Alle Routen sind standardmäßig geschützt. Nicht-authentifizierte Benutzer werden zur Login-Seite weitergeleitet.

### Auth-Context verwenden
```tsx
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { user, isAuthenticated, logout } = useAuth()
  
  if (!isAuthenticated) return null
  
  return (
    <div>
      <p>Hallo, {user?.name}!</p>
      <button onClick={logout}>Abmelden</button>
    </div>
  )
}
```

## Wichtige Hinweise

1. **Passwort-Hashing**: Aktuell wird SHA256 verwendet. In Production sollten Sie bcrypt oder argon2 verwenden.
2. **User Storage**: Aktuell in-memory. In Production sollten Sie eine Datenbank verwenden.
3. **Token Storage**: Tokens werden in localStorage gespeichert. Für höhere Sicherheit können Sie httpOnly Cookies verwenden.
4. **Apple Sign In**: Erfordert Apple Developer Account ($99/Jahr)

## Nächste Schritte

1. ✅ Backend-Endpunkte erstellt
2. ✅ Frontend-Login-Seite erstellt
3. ✅ Auth-Context erstellt
4. ✅ AuthGuard für geschützte Routen
5. ⏳ Google OAuth Credentials konfigurieren
6. ⏳ Microsoft OAuth Credentials konfigurieren
7. ⏳ Apple Sign In Credentials konfigurieren (Optional)
8. ⏳ ENV-Variablen setzen

## Testing

1. Starten Sie den Backend-Server
2. Starten Sie den Frontend-Server
3. Öffnen Sie: `http://localhost:3000/auth/login`
4. Testen Sie Email-Signup/Login
5. Testen Sie Google OAuth (nach Credentials-Setup)
6. Testen Sie Microsoft OAuth (nach Credentials-Setup)
7. Testen Sie Apple Sign In (nach Credentials-Setup, optional)
