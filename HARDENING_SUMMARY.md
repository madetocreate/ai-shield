# AI Shield - Hardening Summary

## 🔒 Durchgeführte Hardening-Maßnahmen (2025-01-18)

### B1: Release Sanitization ✅

**Was geändert:**
- Neues Script: `scripts/sanitize_release.py`
- Entfernt `.env`, `.DS_Store`, sensitive files aus Release-Packages
- Kopiert `.env.example` (ohne echte Werte)

**Warum:**
- `.env` enthält Secrets, darf niemals geteilt werden
- Verhindert versehentliches Leaken von Secrets in Releases

**Rollback:**
- N/A (Script erstellt nur neue Struktur)

**Verwendung:**
```bash
python3 scripts/sanitize_release.py /path/to/source /path/to/sanitized
```

---

### B2: Port-Kollision Fix (OTEL/Jaeger) ✅

**Was geändert:**
- `docker-compose.yml`: `JAEGER_HTTP_PORT` Default von `4318` auf `14318` geändert
- Kommentar hinzugefügt: "Default 14318 to avoid collision with OTEL_HTTP_PORT"

**Warum:**
- OTEL und Jaeger beide auf Port 4318 → Kollision
- Jaeger auf 14318 verschoben (OTEL bleibt auf 4318)

**Rollback:**
- `JAEGER_HTTP_PORT` in `.env` auf `4318` setzen (wenn gewünscht)

**Dateien:**
- `docker-compose.yml`

---

### B3: Apple Sign-In Token Verification ✅

**Was geändert:**
- Neues Modul: `apps/control-plane/app/apple_verify.py`
- Korrekte JWKS-basierte Verifikation mit Signature-Check
- In-Memory JWKS Cache (6h TTL)
- `auth.py` verwendet jetzt `verify_apple_id_token()` statt `jwt.decode(..., verify_signature=False)`

**Warum:**
- Vorher: `verify_signature=False` → unsicher, ermöglicht Token-Fälschung
- Jetzt: Korrekte Verifikation mit Apple JWKS, issuer, audience

**Rollback:**
- In `auth.py` `verify_apple_token()` wieder zu `jwt.decode(..., verify_signature=False)` ändern

**Dateien:**
- `apps/control-plane/app/apple_verify.py` (neu)
- `apps/control-plane/app/auth.py` (geändert)

**ENV:**
- `APPLE_CLIENT_ID` (required)

---

### B4: Docker Compose Production Configuration ✅

**Was geändert:**
- Neue Datei: `docker-compose.prod.yml`
- Gateway und Control-Plane ohne published ports (nur internal network)
- Nur nginx published ports (80/443)
- Images gepinnt für Stabilität

**Warum:**
- Prod-Sicherheit: Rate Limits/Shields nicht umgehbar
- Stabile Versionen (keine `latest` tags)
- Entry Point nur über nginx

**Rollback:**
- `docker-compose.yml` ohne `-f docker-compose.prod.yml` verwenden

**Verwendung:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Dateien:**
- `docker-compose.prod.yml` (neu)

---

## 📁 Geänderte Dateien

### Neue Dateien
- `scripts/sanitize_release.py` - Release-Sanitization Script
- `SECURITY.md` - Security Guidelines & Secrets Management
- `apps/control-plane/app/apple_verify.py` - Apple Token Verification mit JWKS
- `docker-compose.prod.yml` - Production Docker Compose Configuration

### Geänderte Dateien
- `docker-compose.yml` - Port-Kollision Fix (Jaeger 14318)
- `apps/control-plane/app/auth.py` - Apple Token Verification (JWKS)

---

## 🔐 Security Improvements

1. **Apple Token Verification**: Korrekte Signature-Verifikation verhindert Token-Fälschung
2. **Release Sanitization**: Verhindert Secrets-Leakage in Releases
3. **Production Deployment**: Nginx-only Entry Point verhindert Umgehung von Rate Limits/Shields
4. **Port Management**: Keine Port-Kollisionen mehr

---

## 📋 Deployment Checklist

### Development
- [x] `.env` Datei vorhanden (nicht committen!)
- [x] `docker-compose.yml` verwendet (mit published ports)

### Production
- [ ] `docker-compose.prod.yml` verwenden (nginx-only entry point)
- [ ] Images gepinnt (in `docker-compose.prod.yml`)
- [ ] Secrets über Docker Secrets oder sichere Channels
- [ ] `.env` niemals in Images/Releases
- [ ] Apple `APPLE_CLIENT_ID` gesetzt

---

## ⚠️ Wichtige Hinweise

1. **.env niemals teilen** - Verwenden Sie `sanitize_release.py` vor Releases
2. **Keys rotieren** - Wenn `.env` jemals geteilt wurde, sofort alle Keys rotieren
3. **Production Deployment** - Verwenden Sie `docker-compose.prod.yml` für Prod
4. **Apple Verification** - Erfordert `APPLE_CLIENT_ID` ENV Variable

---

**Status:** ✅ Alle Hardening-Maßnahmen implementiert
**Datum:** 2025-01-18

