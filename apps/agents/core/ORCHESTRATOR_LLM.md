# LLM-Based Orchestrator - Intelligente Routing-Entscheidungen

## 🎯 Übersicht

Der **LLMOrchestratorAgent** nutzt ein LLM (GPT-5.2 oder neuestes Modell) für intelligente Routing-Entscheidungen basierend auf OpenAI Agent SDK Patterns.

## 🚀 Warum LLM für Orchestrator?

### Vorteile
1. **Intelligente Entscheidungen**: LLM versteht Kontext und Nuancen
2. **Adaptiv**: Passt sich an neue Situationen an
3. **Kontext-Aware**: Nutzt Konversations-Historie
4. **Reasoning**: Kann komplexe Entscheidungen begründen

### Vergleich

| Aspekt | Logik-basiert | LLM-basiert |
|--------|---------------|-------------|
| **Intelligenz** | ❌ Regel-basiert | ✅ Kontext-verstehend |
| **Adaptivität** | ❌ Statisch | ✅ Dynamisch |
| **Komplexität** | ❌ Begrenzt | ✅ Hoch |
| **Geschwindigkeit** | ✅ Sehr schnell | ⚠️ Etwas langsamer (~300ms) |

## 🔧 Modell-Konfiguration

### Neuestes Modell (Standard)

```bash
# GPT-5.2 (Dezember 2025) - Neuestes Modell
ORCHESTRATOR_MODEL=gpt-5.2
```

### Verfügbare Modelle (Fallback-Kette)

1. **gpt-5.2** (Dezember 2025) - Neuestes, beste Performance
2. **gpt-5.1** (November 2025) - Sehr gut
3. **gpt-5** (August 2025) - Gut
4. **gpt-4.1** (April 2025) - Fallback
5. **gpt-4o** (May 2024) - Letzter Fallback

### Konfiguration

```bash
# In .env Datei
ORCHESTRATOR_MODEL=gpt-5.2

# LLM API Key
OPENAI_API_KEY=sk-...
# Oder via LiteLLM Gateway
LITELLM_MASTER_KEY=...
```

## 📋 OpenAI Agent SDK Pattern

### LLM-Driven Orchestration

Der Orchestrator nutzt **LLM-Driven Orchestration** Pattern:

1. **System Prompt**: Definiert verfügbare Agents und Routing-Regeln
2. **Tools**: Agents als Tools für LLM (route_to_agent, escalate_to_human)
3. **Tool Choice**: LLM wählt autonom passenden Agent
4. **Reasoning**: LLM begründet Entscheidung

### Tool-basierte Agent-Auswahl

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "route_to_agent",
            "description": "Routet zu passendem Agent",
            "parameters": {
                "agent_name": "...",
                "reasoning": "...",
                "confidence": 0.0-1.0
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Eskaliert zu Human",
            ...
        }
    }
]
```

## 🎯 Verwendung

### Standard (nutzt ENV)

```python
from apps.agents.core.llm_orchestrator_agent import get_llm_orchestrator, RoutingRequest

orchestrator = get_llm_orchestrator()  # Nutzt ORCHESTRATOR_MODEL aus ENV

request = RoutingRequest(
    account_id="restaurant-123",
    user_message="Ich möchte einen Tisch für morgen Abend reservieren, aber ich habe eine Allergie",
    channel="phone",
    conversation_history=[
        {"role": "user", "content": "Hallo"},
        {"role": "assistant", "content": "Guten Tag, wie kann ich helfen?"}
    ]
)

response = orchestrator.route(request)

print(f"Agent: {response.target_agent}")
print(f"Reasoning: {response.reasoning}")
print(f"Confidence: {response.confidence}")
```

### Mit Custom LLM Client

```python
import litellm
from apps.agents.core.llm_orchestrator_agent import LLMOrchestratorAgent

orchestrator = LLMOrchestratorAgent(llm_client=litellm)
```

## 🧠 Intelligente Features

### 1. Kontext-Verständnis

```python
# LLM versteht komplexe Anfragen
request = RoutingRequest(
    user_message="Ich war letzte Woche da und hatte ein Problem mit meiner Bestellung. Jetzt möchte ich wieder bestellen, aber diesmal sicherstellen dass es richtig ist."
)

# LLM erkennt:
# - Beschwerde-Kontext (letzte Woche)
# - Aktueller Intent (Bestellung)
# - Routing: Erst Beschwerde lösen, dann Bestellung
```

### 2. Konversations-Historie

```python
request = RoutingRequest(
    user_message="Ja, das passt",
    conversation_history=[
        {"role": "assistant", "content": "Möchten Sie einen Tisch für 4 Personen am Samstag um 19 Uhr?"},
        {"role": "user", "content": "Ja, das passt"}
    ]
)

# LLM versteht Kontext aus Historie
```

### 3. Multi-Intent Erkennung

```python
# Komplexe Anfrage mit mehreren Intents
request = RoutingRequest(
    user_message="Ich möchte einen Tisch reservieren und habe eine Frage zu Allergenen im Menü"
)

# LLM kann entscheiden:
# - Primär: Reservierung → restaurant_voice_host_agent
# - Sekundär: Allergen-Frage kann im gleichen Agent behandelt werden
```

## 📊 Performance

### Mit GPT-5.2

```
LLM Routing-Entscheidung: ~300ms
Agent-Instanziierung: ~10ms
Total: ~310ms
```

### Vergleich mit Logik-basiert

```
Logik-basiert: ~50ms (aber weniger intelligent)
LLM-basiert: ~310ms (aber viel intelligenter)
```

**Trade-off**: Etwas langsamer, aber deutlich intelligenter!

## ⚙️ Konfiguration

### Environment Variables

```bash
# Orchestrator Model
ORCHESTRATOR_MODEL=gpt-5.2

# LLM API
OPENAI_API_KEY=sk-...
# Oder
LITELLM_MASTER_KEY=...
GATEWAY_BASE_URL=http://gateway:4000
```

### Code-Level

```python
import os
os.environ["ORCHESTRATOR_MODEL"] = "gpt-5.2"

orchestrator = get_llm_orchestrator()
```

## 🔍 Monitoring

Routing-Entscheidungen werden automatisch getrackt:

```python
from apps.agents.core.monitoring import get_monitor

monitor = get_monitor()
stats = monitor.get_routing_stats()

# Enthält:
# - Routing-Entscheidungen
# - Confidence-Levels
# - Reasoning (aus LLM)
```

## 🐛 Troubleshooting

### Problem: Modell nicht verfügbar

**Lösung:**
1. Prüfe Modell-Name (gpt-5.2, gpt-5.1, etc.)
2. Nutze Fallback-Kette (automatisch)
3. Prüfe API Key

### Problem: Zu langsam

**Lösung:**
1. Nutze schnelleres Modell (gpt-4o statt gpt-5.2)
2. Reduziere max_tokens
3. Nutze Caching

---

**Version:** 1.0.0  
**Basiert auf:** OpenAI Agent SDK, LLM-Driven Orchestration Pattern
