# MCP Tool Connection - Best Practices

## 📋 Übersicht

Alle Agents sind als MCP Tools registriert und mit ihren Supervisors verbunden.

## ✅ Implementierte Best Practices

### 1. Tool Discovery ✅
- Automatische Discovery aller Agents
- Strukturierte Tool-Definitionen
- Metadata für Supervisor-Verbindungen

### 2. Tool Registration ✅
- Alle Agents als MCP Tools registriert
- Supervisor-Hierarchie dokumentiert
- Package-basiertes Filtering

### 3. Secure Integration ✅
- Tool-Kategorisierung (agent, tool, function)
- Package-basierte Zugriffskontrolle
- Supervisor-Validierung

### 4. Dynamic Tool Management ✅
- Tool-Filtering basierend auf Intent
- Package-basiertes Filtering
- Enable/Disable pro Tool

## 🏗️ Supervisor-Hierarchie

### Gastronomie

```
gastronomy_supervisor_agent (Supervisor)
├── restaurant_voice_host_agent
├── restaurant_takeout_order_agent
├── restaurant_menu_allergen_agent
├── restaurant_events_catering_agent
├── restaurant_reputation_agent
├── restaurant_shift_staffing_agent (V2)
├── restaurant_inventory_procurement_agent (V2)
└── restaurant_daily_ops_report_agent (V2)
```

### Praxis

```
practice_supervisor_agent (Supervisor)
├── practice_phone_reception_agent
├── practice_appointment_reminder_agent
├── practice_patient_intake_forms_agent
├── practice_admin_requests_agent
├── healthcare_privacy_guard_agent
├── practice_clinical_documentation_agent (V2)
├── practice_billing_insurance_agent (V2)
└── practice_document_inbox_agent (V2)
```

### Allgemein

```
support_triage_agent (Supervisor)
└── support_resolution_agent
```

## 🛠️ MCP Tool Format

### Tool Definition

```json
{
  "name": "agent_restaurant_voice_host_agent",
  "description": "Restaurant Voice Host - Reservierungen, Öffnungszeiten...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_message": {"type": "string"},
      "context": {"type": "object"}
    },
    "required": ["user_message"]
  },
  "metadata": {
    "agent_name": "restaurant_voice_host_agent",
    "supervisor": "gastronomy_supervisor_agent",
    "package": "gastronomy",
    "category": "agent"
  }
}
```

## 🔧 Verwendung

### Tools für Orchestrator holen

```python
from apps.agents.core.mcp_tool_registry import get_mcp_tool_registry

mcp_registry = get_mcp_tool_registry()

# Alle Tools
all_tools = mcp_registry.get_tools_for_orchestrator()

# Gefiltert nach Package
gastronomy_tools = mcp_registry.get_tools_for_orchestrator(
    package_type="gastronomy"
)

# Gefiltert nach Intent (vom Intent Agent)
filtered_tools = mcp_registry.get_tools_for_orchestrator(
    filtered_agents=["restaurant_voice_host_agent", "gastronomy_supervisor_agent"]
)
```

### Supervisor-Hierarchie prüfen

```python
hierarchy = mcp_registry.get_supervisor_hierarchy()
# {
#   "gastronomy_supervisor_agent": [
#     "restaurant_voice_host_agent",
#     "restaurant_takeout_order_agent",
#     ...
#   ],
#   ...
# }
```

### Verifikation

```bash
python apps/agents/scripts/verify_supervisor_connections.py
```

## ✅ Verifikation

### Prüft:
- ✅ Alle Agents sind registriert
- ✅ Alle Supervisors existieren
- ✅ Supervisor-Verbindungen sind korrekt
- ✅ MCP Tools sind korrekt definiert

### Output:

```
📊 STATISTIKEN
Total Tools registriert: 18
Status: ok

🏗️ SUPERVISOR-HIERARCHIE
gastronomy_supervisor_agent:
  ✅ restaurant_voice_host_agent
  ✅ restaurant_takeout_order_agent
  ...

✅ KEINE ISSUES
```

## 🔒 Security

### Best Practices implementiert:
- ✅ Tool-Kategorisierung
- ✅ Package-basierte Zugriffskontrolle
- ✅ Supervisor-Validierung
- ✅ Tool-Metadata für Audit

## 📊 Tool-Statistiken

### Gastronomie
- 9 Agents (6 MVP + 3 V2)
- 1 Supervisor
- Alle verbunden ✅

### Praxis
- 9 Agents (6 MVP + 3 V2)
- 1 Supervisor
- Alle verbunden ✅

### Allgemein
- 2 Agents
- 1 Supervisor
- Alle verbunden ✅

**Total: 20 Agents als MCP Tools registriert**

---

**Version:** 1.0.0  
**Basiert auf:** MCP Best Practices 2024/2025
