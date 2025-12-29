# Apple Services Integration Setup

## Übersicht

Dieser Guide erklärt, wie Sie Apple Services (Apple Sign In, iCloud Calendar, iCloud Drive, Apple Push Notifications) über Nango integrieren.

## Verfügbare Apple Services

### 1. Apple Sign In
- **Provider Key**: `apple-signin`
- **OAuth Type**: OAuth 2.0
- **Verwendung**: Apple ID Authentifizierung für Benutzer
- **Scopes**: `name`, `email`

### 2. iCloud Calendar
- **Provider Key**: `icloud-calendar`
- **OAuth Type**: OAuth 2.0 (via iCloud API)
- **Verwendung**: iCloud Kalender lesen und erstellen
- **Scopes**: `calendars.read`, `calendars.write`

### 3. iCloud Drive
- **Provider Key**: `icloud-drive`
- **OAuth Type**: OAuth 2.0 (via iCloud API)
- **Verwendung**: iCloud Drive Dateien verwalten
- **Scopes**: `drive.read`, `drive.write`

### 4. Apple Push Notifications (APNs)
- **Provider Key**: `apple-push-notifications`
- **Auth Type**: Certificate-based (kein OAuth)
- **Verwendung**: Push-Benachrichtigungen an iOS/macOS Geräte senden
- **Scopes**: `notifications.write`

## Setup-Anleitung

### Apple Sign In Setup

1. **Apple Developer Account erstellen**
   - Gehen Sie zu: https://developer.apple.com/
   - Erstellen Sie ein Apple Developer Account (kostenpflichtig: $99/Jahr)

2. **App ID erstellen**
   - Gehen Sie zu: Certificates, Identifiers & Profiles
   - Erstellen Sie eine neue App ID
   - Aktivieren Sie "Sign In with Apple"

3. **Service ID erstellen**
   - Erstellen Sie eine Service ID für Web-Anwendungen
   - Konfigurieren Sie die Redirect URLs:
     - `https://api.nango.dev/oauth/callback` (für Nango Cloud)
     - `http://localhost:3003/oauth/callback` (für lokales Nango)

4. **OAuth Credentials**
   - Erstellen Sie einen Key für "Sign In with Apple"
   - Laden Sie die `.p8` Key-Datei herunter
   - Notieren Sie die Key ID und Team ID

5. **Nango konfigurieren**
   - Provider Key: `apple-signin`
   - Authorization URL: `https://appleid.apple.com/auth/authorize`
   - Token URL: `https://appleid.apple.com/auth/token`
   - Client ID: Ihre Service ID
   - Client Secret: Generiert aus Key ID, Team ID und `.p8` Key
   - Scopes: `name email`

### iCloud Calendar Setup

1. **iCloud API Zugriff**
   - Apple bietet keine direkte öffentliche iCloud API
   - **Alternative**: CalDAV verwenden (nicht OAuth)
   - **Oder**: Apple Developer Enterprise Account für iCloud API

2. **CalDAV Integration** (Alternative)
   - iCloud Calendar nutzt CalDAV-Protokoll
   - Erfordert App-spezifisches Passwort von iCloud
   - Nicht direkt über OAuth möglich

3. **Nango Custom Provider**
   - Erstellen Sie einen Custom Provider in Nango
   - Verwenden Sie CalDAV-Endpunkte:
     - `https://caldav.icloud.com/` (für Kalender)
   - **Hinweis**: CalDAV erfordert spezielle Konfiguration

### iCloud Drive Setup

1. **iCloud API Zugriff**
   - Ähnlich wie iCloud Calendar
   - Keine direkte öffentliche API verfügbar
   - Erfordert Apple Developer Enterprise Account

2. **Alternative: WebDAV**
   - iCloud Drive nutzt WebDAV-Protokoll
   - Endpoint: `https://www.icloud.com/webdav/`
   - Erfordert App-spezifisches Passwort

3. **Nango Custom Provider**
   - Erstellen Sie einen Custom Provider
   - Konfigurieren Sie WebDAV-Authentifizierung
   - **Hinweis**: WebDAV ist nicht OAuth-kompatibel

### Apple Push Notifications (APNs) Setup

1. **Apple Developer Account**
   - Erstellen Sie ein Apple Developer Account
   - Gehen Sie zu: Certificates, Identifiers & Profiles

2. **APNs Key erstellen**
   - Erstellen Sie einen APNs Authentication Key
   - Laden Sie die `.p8` Key-Datei herunter
   - Notieren Sie die Key ID und Team ID

3. **App ID konfigurieren**
   - Erstellen Sie eine App ID
   - Aktivieren Sie "Push Notifications"
   - Erstellen Sie ein Provisioning Profile

4. **Nango konfigurieren**
   - **Wichtig**: APNs verwendet KEIN OAuth
   - APNs nutzt JWT-basierte Authentifizierung
   - Erfordert Custom Integration in Nango
   - Oder direkte Integration in Backend

5. **Backend-Integration** (Empfohlen)
   - APNs ist besser direkt im Backend integriert
   - Verwenden Sie `pyapns2` oder ähnliche Bibliotheken
   - Authentifizierung via JWT mit `.p8` Key

## Wichtige Hinweise

### Apple Sign In
- ✅ **Vollständig unterstützt** über OAuth 2.0
- ✅ Kann direkt über Nango konfiguriert werden
- ✅ Funktioniert mit Standard OAuth Flow

### iCloud Calendar & Drive
- ⚠️ **Eingeschränkt verfügbar**
- ⚠️ Apple bietet keine öffentliche OAuth API für iCloud
- ⚠️ Erfordert CalDAV/WebDAV (nicht OAuth-kompatibel)
- ⚠️ Alternative: Apple Developer Enterprise Account

### Apple Push Notifications
- ⚠️ **Kein OAuth**
- ⚠️ Nutzt JWT-basierte Authentifizierung
- ⚠️ Besser direkt im Backend integriert
- ✅ Kann über Custom Nango Provider konfiguriert werden

## Alternative Lösungen

### Für iCloud Calendar:
1. **Google Calendar** (bereits integriert) - Alternative zu iCloud
2. **Microsoft 365 Calendar** (bereits integriert) - Alternative zu iCloud
3. **CalDAV direkt** - Erfordert Custom Backend-Integration

### Für iCloud Drive:
1. **Google Drive** (bereits integriert) - Alternative zu iCloud Drive
2. **Microsoft OneDrive** - Kann über Microsoft 365 integriert werden
3. **WebDAV direkt** - Erfordert Custom Backend-Integration

## Beispiel-Konfiguration für Nango

### Apple Sign In (Funktioniert direkt)
```yaml
provider_key: apple-signin
authorization_url: https://appleid.apple.com/auth/authorize
token_url: https://appleid.apple.com/auth/token
client_id: com.yourcompany.yourapp
client_secret: [JWT-basiertes Secret]
scopes: name email
```

### iCloud Calendar (CalDAV - Custom)
```yaml
provider_key: icloud-calendar
type: caldav
base_url: https://caldav.icloud.com/
username: [iCloud E-Mail]
password: [App-spezifisches Passwort]
```

## API-Dokumentationen

- **Apple Sign In**: https://developer.apple.com/sign-in-with-apple/
- **APNs**: https://developer.apple.com/documentation/usernotifications
- **iCloud API**: Nur für Enterprise Accounts verfügbar
- **CalDAV**: https://tools.ietf.org/html/rfc4791

## Empfehlung

Für die meisten Anwendungsfälle empfehlen wir:
1. **Apple Sign In** ✅ - Vollständig über Nango integrierbar
2. **Apple Push Notifications** ✅ - Direkt im Backend integrieren
3. **iCloud Calendar/Drive** ⚠️ - Verwenden Sie stattdessen Google/Microsoft Services

## Nächste Schritte

1. Apple Developer Account erstellen
2. App ID und Service ID konfigurieren
3. Apple Sign In in Nango konfigurieren
4. APNs direkt im Backend integrieren (falls benötigt)
5. Für iCloud: Alternative Services (Google/Microsoft) verwenden
