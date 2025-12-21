# AI Shield - Security Guidelines

## 🔒 Secrets Management

### .env Datei

**WICHTIG: `.env` Datei niemals teilen oder committen!**

- Die `.env` Datei enthält sensible Variablen (API Keys, Passwörter, Secrets)
- Sie ist bereits in `.gitignore` aufgenommen
- **Trotzdem**: Bei Release/Package-Erstellung kann `.env` versehentlich enthalten sein

### Release-Sanitization

**Verwenden Sie das Sanitize-Script vor dem Teilen von Code/Releases:**

```bash
# Script erstellt eine sichere Kopie ohne .env
python3 scripts/sanitize_release.py /path/to/source /path/to/sanitized

# Dry-run (zeigt was entfernt würde, ohne zu kopieren)
python3 scripts/sanitize_release.py /path/to/source --dry-run
```

**Was das Script entfernt:**
- `.env` Dateien
- `.DS_Store` (macOS metadata)
- `__pycache__`, `*.pyc` (Python cache)
- Sensitive log files
- Editor temporäre Dateien

**Was das Script behält:**
- `.env.example` (Template ohne echte Werte)
- Source Code
- Konfigurationsdateien (ohne Secrets)

### Wenn Secrets geteilt wurden

**Sofortige Maßnahmen:**
1. **Keys rotieren** - Alle betroffenen API Keys, Passwörter und Secrets sofort ändern
2. **Audit Logs prüfen** - Prüfen Sie, ob jemand die Keys verwendet hat
3. **Betroffene Services benachrichtigen** - Wenn Keys für externe Services verwendet werden

**Rotation-Checkliste:**
- [ ] Database Passwords
- [ ] API Keys (OpenAI, Anthropic, etc.)
- [ ] JWT Secrets
- [ ] OAuth Client Secrets (Google, Apple, Microsoft)
- [ ] Langfuse Secrets
- [ ] Control Plane Admin Keys
- [ ] Gateway Admin Keys

### Docker Secrets (Empfehlung für Production)

Für Production-Deployments sollten Secrets über Docker Secrets verwaltet werden:

```yaml
# docker-compose.yml
services:
  gateway:
    secrets:
      - openai_api_key
      - database_password

secrets:
  openai_api_key:
    external: true
  database_password:
    file: ./secrets/db_password.txt
```

**Vorteile:**
- Secrets werden nicht in Images eingebettet
- Zugriff nur für Services, die sie benötigen
- Zentralisiertes Management
- Audit-Trail möglich

### .env.example

Die `.env.example` Datei sollte:
- ✅ Alle benötigten Variablen auflisten
- ✅ Beispielwerte (Placeholder) enthalten
- ✅ Kommentare mit Beschreibungen haben
- ❌ Niemals echte Secrets enthalten
- ❌ Niemals echte Passwörter enthalten

**Beispiel:**
```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Database Password
DATABASE_PASSWORD=your-secure-password

# JWT Secret (mindestens 32 Zeichen)
JWT_SECRET=change-me-to-random-secret-min-32-chars
```

## 🔐 Best Practices

1. **Never commit secrets** - Verwenden Sie `.gitignore` für `.env`
2. **Rotate regularly** - Passwörter/Keys regelmäßig wechseln
3. **Use strong secrets** - Mindestens 32 Zeichen für JWT Secrets
4. **Limit access** - Nur notwendige Personen/Service haben Zugriff
5. **Monitor usage** - Audit-Logs für API-Keys prüfen
6. **Use secrets management** - In Production: Docker Secrets, AWS Secrets Manager, etc.

## 📋 Security Checklist

Vor jedem Release:
- [ ] `.env` in `.gitignore` (verifizieren)
- [ ] Sanitize-Script ausführen
- [ ] Keine Secrets in Code/Kommentaren
- [ ] `.env.example` aktuell (ohne echte Werte)
- [ ] Docker Images enthalten keine Secrets
- [ ] Production-Secrets über sichere Channels verteilt

---

**Letzte Aktualisierung:** 2025-01-18

