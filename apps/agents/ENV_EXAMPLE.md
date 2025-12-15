# Environment Variables - Branchen-Pakete

## 📋 Übersicht

Beispiel `.env` Datei für die Branchen-Pakete.

---

## 🔧 Intent Agent Konfiguration

```bash
# Intent Agent Model (für schnelle Intent-Erkennung)
# Standard: gpt-4o-mini (schnell, günstig)
# Alternative: gpt-4o (etwas langsamer, aber präziser)
INTENT_AGENT_MODEL=gpt-4o-mini
```

---

## 🔑 LLM API Keys

### Option 1: OpenAI direkt

```bash
# OpenAI API Key (für Intent Agent)
OPENAI_API_KEY=sk-...
```

### Option 2: Via LiteLLM Gateway

```bash
# LiteLLM Master Key (für Gateway)
LITELLM_MASTER_KEY=your-master-key

# Gateway URL (falls nicht localhost)
GATEWAY_BASE_URL=http://gateway:4000
```

---

## 📦 Package Manifest Storage

```bash
# Storage Path für Package Manifests (optional)
# Default: /app/data/manifests
MANIFEST_STORAGE_PATH=/app/data/manifests
```

---

## 🔒 Consent & Redaction

```bash
# Retention Policy (Tage)
# Default: Keine Retention (unbegrenzt)
# Praxis: 365 (1 Jahr für Gesundheitsdaten)
DEFAULT_RETENTION_DAYS=90
```

---

## 📊 Monitoring

```bash
# Prometheus Metrics Endpoint (optional)
# Default: /metrics
METRICS_ENDPOINT=/metrics
```

---

## 🎯 Vollständige .env Beispiel

```bash
# ============================================
# Intent Agent Configuration
# ============================================
INTENT_AGENT_MODEL=gpt-4o-mini

# ============================================
# LLM API Keys
# ============================================
# Option 1: OpenAI direkt
OPENAI_API_KEY=sk-...

# Option 2: Via LiteLLM Gateway
LITELLM_MASTER_KEY=your-master-key
GATEWAY_BASE_URL=http://gateway:4000

# ============================================
# Package Manifest Storage
# ============================================
MANIFEST_STORAGE_PATH=/app/data/manifests

# ============================================
# Consent & Redaction
# ============================================
DEFAULT_RETENTION_DAYS=90

# ============================================
# Monitoring
# ============================================
METRICS_ENDPOINT=/metrics
```

---

## 🔍 Prüfen der Konfiguration

```bash
# Prüfe alle ENV Variables
python -c "
import os
print('INTENT_AGENT_MODEL:', os.getenv('INTENT_AGENT_MODEL', 'gpt-4o-mini (default)'))
print('OPENAI_API_KEY:', '✅ gesetzt' if os.getenv('OPENAI_API_KEY') else '❌ nicht gesetzt')
print('LITELLM_MASTER_KEY:', '✅ gesetzt' if os.getenv('LITELLM_MASTER_KEY') else '❌ nicht gesetzt')
"
```

---

**Version:** 1.0.0
