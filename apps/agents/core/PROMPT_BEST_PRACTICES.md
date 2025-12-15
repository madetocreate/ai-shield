# Prompt Best Practices - Orchestrator & Agents

## 📋 Übersicht

Basierend auf OpenAI Best Practices 2024/2025 und Recherche-Ergebnissen.

## ✅ Implementierte Best Practices

### 1. Klarheit und Spezifität ✅
- Klare Struktur mit Delimitern (`##`, `###`)
- Spezifische Anweisungen für jeden Agent
- Präzise Tool-Beschreibungen

### 2. Modulare Architektur ✅
- `OrchestratorPromptBuilder` - Separater Builder
- `IntentAgentPromptBuilder` - Separater Builder
- Wiederverwendbare Templates

### 3. Strukturierte Outputs ✅
- JSON-Format für Intent-Erkennung
- Tool-basierte Funktionen für Routing
- Klare Parameter-Definitionen

### 4. Tool Filtering ✅
- Intent Agent filtert Agents
- Orchestrator bekommt nur relevante Tools
- Reduzierte Tool-Auswahl = bessere Entscheidungen

### 5. Web Search Integration ✅
- Direkte Web-Search-Funktion für Orchestrator
- Für aktuelle Informationen, Verifikationen

## 🎯 Orchestrator Prompt Struktur

```
# ORCHESTRATOR SYSTEM PROMPT

## DEINE ROLLE
[Klare Rollen-Definition]

## VERFÜGBARE AGENTS
[Strukturierte Agent-Liste mit Beschreibungen]

## ROUTING-REGELN
[Spezifische Regeln]

## TOOLS
[Tool-Beschreibungen]

## DECISION PROCESS
[Schritt-für-Schritt Prozess]

## BEISPIELE
[Few-Shot Examples]

## SECURITY & COMPLIANCE
[Security Guidelines]
```

## 🔧 Intent Agent Prompt

- **Strukturiert**: Klare Intent-Liste
- **JSON-Format**: Strukturierte Ausgabe
- **Entity Extraction**: Zusätzliche Informationen
- **Filtering**: Empfohlene Agents für Orchestrator

## 🛠️ Tool Filtering

### Vorher (ohne Filtering)
```
Orchestrator hat 15+ Agents als Tools
→ LLM hat zu viele Optionen
→ Langsamere Entscheidungen
→ Weniger präzise
```

### Nachher (mit Filtering)
```
Intent Agent filtert → 2-3 relevante Agents
→ Orchestrator hat nur relevante Tools
→ Schnellere, präzisere Entscheidungen
```

## 🌐 Web Search Integration

### Tool Definition

```python
{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Suche im Internet nach aktuellen Informationen...",
        "parameters": {
            "query": "...",
            "reason": "..."
        }
    }
}
```

### Verwendung

1. **Orchestrator erkennt**: Braucht aktuelle Infos
2. **Ruft web_search auf**: Sucht nach Informationen
3. **Nutzt Ergebnisse**: Für Routing-Entscheidung

### Beispiele

- "Sind die Öffnungszeiten heute korrekt?" → Web Search → Verifikation
- "Gibt es heute Events?" → Web Search → Aktuelle Events
- "Was sagt Google Reviews?" → Web Search → Reviews prüfen

## 📊 Performance-Verbesserung

### Mit Tool Filtering

```
Intent Agent: ~200ms (filtert Agents)
Orchestrator: ~150ms (weniger Tools = schneller)
Total: ~350ms (vs. ~500ms ohne Filtering)
```

### Mit Web Search

```
Orchestrator: ~150ms (erkennt Web Search nötig)
Web Search: ~500ms (externe API)
Orchestrator: ~150ms (nutzt Ergebnisse)
Total: ~800ms (aber mit aktuellen Infos!)
```

## 🔒 Security Considerations

1. **Input Filtering**: Redaction vor LLM-Call
2. **Tool Access**: Nur relevante Tools verfügbar
3. **Output Validation**: Strukturierte Outputs
4. **Error Handling**: Fallback-Mechanismen

## 📝 Prompt-Templates

### OrchestratorPromptBuilder

```python
from apps.agents.core.prompt_templates import OrchestratorPromptBuilder

prompt = OrchestratorPromptBuilder.build_system_prompt(
    available_agents=agents,
    package_type="gastronomy"
)
```

### IntentAgentPromptBuilder

```python
from apps.agents.core.prompt_templates import IntentAgentPromptBuilder

prompt = IntentAgentPromptBuilder.build_system_prompt()
```

## 🎓 Best Practices Checklist

- ✅ Klare Struktur mit Delimitern
- ✅ Spezifische Anweisungen
- ✅ Tool-Beschreibungen
- ✅ Few-Shot Examples
- ✅ Security Guidelines
- ✅ Tool Filtering
- ✅ Web Search Integration
- ✅ Strukturierte Outputs

---

**Version:** 1.0.0  
**Basiert auf:** OpenAI Best Practices 2024/2025
