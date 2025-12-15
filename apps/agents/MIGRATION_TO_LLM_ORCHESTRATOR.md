# Migration zu LLM-Based Orchestrator

## 🎯 Warum Migration?

Der **LLMOrchestratorAgent** ist deutlich intelligenter als der logik-basierte Orchestrator:

- ✅ **Intelligente Routing-Entscheidungen** mit LLM (GPT-5.2)
- ✅ **Kontext-Verständnis** (Konversations-Historie)
- ✅ **Adaptiv** (passt sich an neue Situationen an)
- ✅ **OpenAI Agent SDK Pattern** (LLM-Driven Orchestration)

## 🔄 Migration

### Schritt 1: Gateway Config aktualisieren

```yaml
# apps/gateway/config.yaml
model_list:
  - model_name: gpt-5.2  # ✅ Neuestes Modell
    litellm_params:
      model: openai/gpt-5.2
      api_key: os.environ/OPENAI_API_KEY
```

### Schritt 2: Environment Variable setzen

```bash
# In .env Datei
ORCHESTRATOR_MODEL=gpt-5.2
```

### Schritt 3: Code aktualisieren

**Vorher (Logik-basiert):**
```python
from apps.agents.core.global_orchestrator_agent import get_orchestrator

orchestrator = get_orchestrator()  # Logik-basiert
```

**Nachher (LLM-basiert):**
```python
from apps.agents.core.llm_orchestrator_agent import get_llm_orchestrator

orchestrator = get_llm_orchestrator()  # LLM-basiert (GPT-5.2)
```

### Schritt 4: Testing

```python
# Test intelligente Routing-Entscheidung
request = RoutingRequest(
    account_id="restaurant-123",
    user_message="Ich möchte einen Tisch reservieren, aber ich habe eine Frage zu Allergenen",
    channel="phone"
)

response = orchestrator.route(request)

# LLM sollte erkennen:
# - Primär: Reservierung
# - Sekundär: Allergen-Frage
# - Routing: restaurant_voice_host_agent (kann beides)
```

## 📊 Vergleich

| Feature | Logik-basiert | LLM-basiert |
|---------|---------------|-------------|
| **Intelligenz** | ❌ Regel-basiert | ✅ Kontext-verstehend |
| **Geschwindigkeit** | ✅ ~50ms | ⚠️ ~310ms |
| **Komplexität** | ❌ Begrenzt | ✅ Hoch |
| **Adaptivität** | ❌ Statisch | ✅ Dynamisch |
| **Reasoning** | ❌ Kein | ✅ Ja |

## ⚠️ Wichtige Hinweise

1. **Performance**: LLM-basiert ist etwas langsamer (~310ms vs ~50ms)
2. **Kosten**: LLM-Calls kosten Geld (aber minimal mit gpt-5.2)
3. **Fallback**: Automatischer Fallback zu Logik-basiert bei Fehlern

## 🔧 Konfiguration

### Modell-Auswahl

```bash
# Neuestes (empfohlen)
ORCHESTRATOR_MODEL=gpt-5.2

# Etwas älter (schneller)
ORCHESTRATOR_MODEL=gpt-5.1

# Fallback
ORCHESTRATOR_MODEL=gpt-4o
```

### Monitoring

```python
# Routing-Entscheidungen werden automatisch getrackt
from apps.agents.core.monitoring import get_monitor

monitor = get_monitor()
stats = monitor.get_routing_stats()
# Enthält Reasoning aus LLM
```

---

**Version:** 1.0.0
