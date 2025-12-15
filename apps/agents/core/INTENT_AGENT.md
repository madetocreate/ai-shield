# Intent Agent - Schnelle Intent-Erkennung

## Übersicht

Der **Intent Agent** erkennt den Intent einer Benutzer-Nachricht **BEVOR** der Orchestrator routet. Das macht das Routing viel schneller und präziser.

## 🚀 Vorteile

1. **Schneller**: Intent wird einmal erkannt, nicht mehrfach in jedem Supervisor
2. **Präziser**: LLM-basierte Erkennung statt Keyword-Matching
3. **Direktes Routing**: Bei hoher Confidence (>0.8) überspringt Orchestrator Supervisor
4. **Entity Extraction**: Erkennt auch Entities (Datum, Zeit, etc.) direkt

## 🔧 Modell

**Standard:** `gpt-4o-mini`
- Schnell (niedrige Latency)
- Günstig
- Gute Intent-Erkennung

**Konfiguration:**
```bash
export INTENT_AGENT_MODEL="gpt-4o-mini"  # Default
# Oder:
export INTENT_AGENT_MODEL="gpt-4o"  # Für bessere Genauigkeit
```

## 📊 Performance

### Mit Intent Agent (NEU)
```
User Message → Intent Agent (gpt-4o-mini, ~200ms) → Direktes Routing → Agent
Total: ~250ms
```

### Ohne Intent Agent (ALT)
```
User Message → Supervisor → Keyword-Matching → Routing → Agent
Total: ~500ms+ (langsamer, weniger präzise)
```

## 🎯 Verwendung

### Automatisch im Orchestrator

Der Orchestrator nutzt den Intent Agent automatisch:

```python
from apps.agents.core.global_orchestrator_agent import get_orchestrator, RoutingRequest

orchestrator = get_orchestrator()  # Intent Agent wird automatisch initialisiert

request = RoutingRequest(
    account_id="restaurant-123",
    user_message="Ich möchte einen Tisch für morgen reservieren",
    channel="phone"
)

response = orchestrator.route(request)
# Intent wird automatisch erkannt und für Routing genutzt
```

### Manuell

```python
from apps.agents.core.intent_agent import get_intent_agent

intent_agent = get_intent_agent()

result = intent_agent.detect_intent(
    user_message="Ich möchte bestellen",
    account_id="restaurant-123"
)

print(f"Intent: {result.intent}")
print(f"Confidence: {result.confidence}")
print(f"Entities: {result.entities}")
```

## 📋 Erkannte Intents

### Gastronomie
- `reservation` - Reservierung
- `takeout_order` - Bestellung
- `allergen_query` - Allergen-Anfrage
- `event_catering` - Event/Catering
- `menu_query` - Menü-Anfrage
- `general_info` - Allgemeine Infos
- `complaint` - Beschwerde
- `review` - Review

### Praxis
- `appointment` - Termin
- `prescription` - Rezept
- `referral` - Überweisung
- `form_request` - Formular
- `billing` - Rechnung
- `symptom_query` - Symptom (→ Safety Check!)
- `admin_request` - Admin-Anfrage

## 🔄 Routing-Strategie

### Direktes Routing (Confidence > 0.8)
```
Intent erkannt → Direkt zu Agent (überspringt Supervisor)
```

### Supervisor-Routing (Confidence ≤ 0.8)
```
Intent erkannt → Supervisor (nutzt Intent als Hinweis) → Agent
```

## ⚙️ Konfiguration

### LLM Client

```python
# Mit LiteLLM
import litellm
orchestrator = GlobalOrchestratorAgent(llm_client=litellm)

# Mit OpenAI direkt
import openai
orchestrator = GlobalOrchestratorAgent(llm_client=openai)
```

### Fallback

Wenn kein LLM verfügbar ist, nutzt der Intent Agent Keyword-Matching als Fallback.

## 📊 Monitoring

Intent-Erkennung wird automatisch getrackt:

```python
from apps.agents.core.monitoring import get_monitor

monitor = get_monitor()
stats = monitor.get_routing_stats()
# Enthält auch Intent-Statistiken
```

## 🐛 Troubleshooting

### Intent Agent nutzt Fallback

**Problem:** Keyword-Matching statt LLM

**Lösung:**
1. Prüfe ob LLM Client verfügbar ist
2. Prüfe Environment Variables (OPENAI_API_KEY, etc.)
3. Prüfe Logs für Fehler

### Niedrige Confidence

**Problem:** Intent wird nicht sicher erkannt

**Lösung:**
1. Nutze besseres Modell (gpt-4o statt gpt-4o-mini)
2. Prüfe User-Message (zu kurz/unklar?)
3. Supervisor wird trotzdem genutzt (Fallback)

---

**Version:** 1.0.0
