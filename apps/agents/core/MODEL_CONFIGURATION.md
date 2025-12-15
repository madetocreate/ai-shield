# Model Configuration - Orchestrator & Intent Agent

## 📊 Übersicht

### Orchestrator
**Modell:** ❌ **KEIN LLM** (rein logik-basiert)
- Der Orchestrator selbst nutzt kein LLM
- Er ist rein logik-basiert (Routing, Manifest-Checks, etc.)
- Sehr schnell (< 10ms)

### Intent Agent
**Modell:** ✅ **LLM** (konfigurierbar via ENV)
- Wird vom Orchestrator genutzt für Intent-Erkennung
- Standard: `gpt-4o-mini`
- Konfigurierbar via Environment Variable

---

## ⚙️ Konfiguration

### Environment Variable

```bash
# In .env Datei oder als Environment Variable
INTENT_AGENT_MODEL=gpt-4o-mini  # Default (schnell, günstig)
```

### Verfügbare Modelle

```bash
# Schnell & Günstig (empfohlen für Intent-Erkennung)
INTENT_AGENT_MODEL=gpt-4o-mini

# Etwas langsamer, aber präziser
INTENT_AGENT_MODEL=gpt-4o

# Andere Modelle (falls über LiteLLM verfügbar)
INTENT_AGENT_MODEL=claude-3-haiku-20240307
INTENT_AGENT_MODEL=gemini/gemini-pro
```

### Beispiel .env Datei

```bash
# Intent Agent Model Configuration
INTENT_AGENT_MODEL=gpt-4o-mini

# LLM API Keys (für Intent Agent)
OPENAI_API_KEY=sk-...
# Oder via LiteLLM Gateway
LITELLM_MASTER_KEY=...
```

---

## 🔧 Code-Level Konfiguration

### Standard (nutzt ENV)

```python
from apps.agents.core.global_orchestrator_agent import get_orchestrator

# Nutzt automatisch INTENT_AGENT_MODEL aus ENV
orchestrator = get_orchestrator()
```

### Mit Custom LLM Client

```python
import litellm
from apps.agents.core.global_orchestrator_agent import GlobalOrchestratorAgent

# Custom LLM Client übergeben
orchestrator = GlobalOrchestratorAgent(llm_client=litellm)
```

### Intent Agent direkt konfigurieren

```python
import os
from apps.agents.core.intent_agent import IntentAgent

# Modell via ENV setzen
os.environ["INTENT_AGENT_MODEL"] = "gpt-4o"

# Intent Agent erstellen
intent_agent = IntentAgent()
```

---

## 📋 Modell-Auswahl

### gpt-4o-mini (Standard) ✅ Empfohlen
- **Geschwindigkeit:** Sehr schnell (~200ms)
- **Kosten:** Sehr günstig
- **Genauigkeit:** Gut für Intent-Erkennung
- **Use Case:** Production (Standard)

### gpt-4o
- **Geschwindigkeit:** Schnell (~300ms)
- **Kosten:** Teurer als mini
- **Genauigkeit:** Sehr gut
- **Use Case:** Wenn höhere Genauigkeit benötigt wird

### Andere Modelle
- Über LiteLLM Gateway verfügbar
- Müssen in `apps/gateway/config.yaml` konfiguriert sein

---

## 🔍 Prüfen welches Modell genutzt wird

### Code-Level

```python
from apps.agents.core.intent_agent import get_intent_agent

intent_agent = get_intent_agent()
print(f"Modell: {intent_agent.model}")
print(f"LLM Client: {intent_agent.llm_client}")
```

### Environment Check

```bash
# Prüfe ENV Variable
echo $INTENT_AGENT_MODEL

# Oder in Python
python -c "import os; print(os.getenv('INTENT_AGENT_MODEL', 'gpt-4o-mini (default)'))"
```

---

## 🚀 Performance

### Mit gpt-4o-mini (Standard)
```
Intent-Erkennung: ~200ms
Orchestrator Routing: ~10ms
Total: ~210ms
```

### Mit gpt-4o
```
Intent-Erkennung: ~300ms
Orchestrator Routing: ~10ms
Total: ~310ms
```

### Ohne LLM (Fallback)
```
Keyword-Matching: ~50ms
Orchestrator Routing: ~10ms
Total: ~60ms (aber weniger präzise!)
```

---

## ⚠️ Wichtige Hinweise

1. **Orchestrator nutzt kein LLM** - er ist rein logik-basiert
2. **Intent Agent nutzt LLM** - konfigurierbar via ENV
3. **Default ist gpt-4o-mini** - wenn ENV nicht gesetzt
4. **Fallback zu Keyword-Matching** - wenn kein LLM verfügbar
5. **LiteLLM wird bevorzugt** - falls verfügbar, sonst OpenAI direkt

---

## 🔧 Troubleshooting

### Problem: Intent Agent nutzt Fallback

**Symptom:** Keyword-Matching statt LLM

**Lösung:**
1. Prüfe `INTENT_AGENT_MODEL` ENV Variable
2. Prüfe `OPENAI_API_KEY` oder `LITELLM_MASTER_KEY`
3. Prüfe ob LiteLLM/OpenAI installiert ist
4. Prüfe Logs für Fehler

### Problem: Falsches Modell wird genutzt

**Lösung:**
1. Prüfe ENV Variable: `echo $INTENT_AGENT_MODEL`
2. Setze explizit: `export INTENT_AGENT_MODEL=gpt-4o`
3. Restart Application

---

## 📝 Zusammenfassung

| Komponente | LLM? | Modell | Konfiguration |
|------------|------|--------|---------------|
| **Orchestrator** | ❌ Nein | - | - |
| **Intent Agent** | ✅ Ja | `gpt-4o-mini` (Default) | `INTENT_AGENT_MODEL` ENV |

**Konfiguration:** Via `.env` Datei oder Environment Variable `INTENT_AGENT_MODEL`

---

**Version:** 1.0.0
