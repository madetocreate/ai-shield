"""
MCP Tool Registry - Registriert alle Agents als MCP Tools

Basiert auf MCP Best Practices:
- Tool Discovery
- Tool Registration
- Secure Integration
- Dynamic Tool Management
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json

from apps.agents.core.agent_registry import get_registry as get_agent_registry


@dataclass
class MCPToolDefinition:
    """MCP Tool Definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    agent_name: str
    supervisor: Optional[str] = None  # Supervisor-Agent
    package: Optional[str] = None  # gastronomy, practice, general
    category: str = "agent"  # agent, tool, function
    enabled: bool = True


class MCPToolRegistry:
    """
    MCP Tool Registry
    
    Registriert alle Agents als MCP Tools für Orchestrator.
    Basiert auf MCP Best Practices.
    """
    
    def __init__(self):
        self.agent_registry = get_agent_registry()
        self.tools: Dict[str, MCPToolDefinition] = {}
        self._register_all_agents_as_tools()
    
    def _register_all_agents_as_tools(self):
        """Registriert alle Agents als MCP Tools"""
        
        # Gastronomie-Agents
        self._register_gastronomy_agents()
        
        # Praxis-Agents
        self._register_practice_agents()
        
        # Allgemeine Agents
        self._register_general_agents()
    
    def _register_gastronomy_agents(self):
        """Registriert Gastronomie-Agents als Tools"""
        supervisor = "gastronomy_supervisor_agent"
        
        agents = [
            {
                "name": "gastronomy_supervisor_agent",
                "description": "Gastronomie Supervisor - routet Gastro-Anfragen intelligent an spezialisierte Agents",
                "supervisor": None,  # Ist selbst Supervisor
                "package": "gastronomy"
            },
            {
                "name": "restaurant_voice_host_agent",
                "description": "Restaurant Voice Host - Reservierungen, Öffnungszeiten, Adresse, allgemeine Infos",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            {
                "name": "restaurant_takeout_order_agent",
                "description": "Takeout Bestellungen - Bestellungen zum Mitnehmen aufnehmen, Upselling, POS-Integration",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            {
                "name": "restaurant_menu_allergen_agent",
                "description": "Allergen-Auskünfte - Allergene, Diäten (vegan, glutenfrei), Menü-Infos, rechtssichere Auskünfte",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            {
                "name": "restaurant_events_catering_agent",
                "description": "Events & Catering - Gruppenbuchungen, Catering-Anfragen, Event-Planung, Angebote",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            {
                "name": "restaurant_reputation_agent",
                "description": "Review-Management - Reviews verwalten, Antworten generieren, Reputation überwachen",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            # V2 Agents
            {
                "name": "restaurant_shift_staffing_agent",
                "description": "Schichtplanung - Schichtplanung, Ausfälle, Ersatz finden",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            {
                "name": "restaurant_inventory_procurement_agent",
                "description": "Bestandsverwaltung - Inventar prüfen, Nachbestellung, Lieferanten",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
            {
                "name": "restaurant_daily_ops_report_agent",
                "description": "Tagesabschlussberichte - Tagesstatistiken, Reports generieren",
                "supervisor": supervisor,
                "package": "gastronomy"
            },
        ]
        
        for agent_info in agents:
            self._register_agent_tool(agent_info)
    
    def _register_practice_agents(self):
        """Registriert Praxis-Agents als Tools"""
        supervisor = "practice_supervisor_agent"
        
        agents = [
            {
                "name": "practice_supervisor_agent",
                "description": "Praxis Supervisor - routet Praxis-Anfragen mit Safety-Check intelligent an spezialisierte Agents",
                "supervisor": None,  # Ist selbst Supervisor
                "package": "practice"
            },
            {
                "name": "practice_phone_reception_agent",
                "description": "Praxis Empfang - Termine buchen/verschieben/stornieren, Öffnungszeiten, Safety-Routing",
                "supervisor": supervisor,
                "package": "practice"
            },
            {
                "name": "practice_appointment_reminder_agent",
                "description": "Terminerinnerungen - No-Show-Reduktion, Reminder senden, Bestätigungen, Warteliste",
                "supervisor": supervisor,
                "package": "practice"
            },
            {
                "name": "practice_patient_intake_forms_agent",
                "description": "Patienten-Formulare - digitale Formulare, Anamnese, Einverständnis, Vorbereitung",
                "supervisor": supervisor,
                "package": "practice"
            },
            {
                "name": "practice_admin_requests_agent",
                "description": "Admin-Anfragen - Rezepte, Überweisungen, AU, Befundkopie, Routine-Anliegen",
                "supervisor": supervisor,
                "package": "practice"
            },
            {
                "name": "healthcare_privacy_guard_agent",
                "description": "Privacy Guard - DSGVO-Compliance, Schweigepflicht, minimale Datenerhebung, Retention",
                "supervisor": supervisor,
                "package": "practice"
            },
            # V2 Agents
            {
                "name": "practice_clinical_documentation_agent",
                "description": "Klinische Dokumentation - Doku-Entwürfe für Behandler, Arztbriefe, Überweisungen",
                "supervisor": supervisor,
                "package": "practice"
            },
            {
                "name": "practice_billing_insurance_agent",
                "description": "Rechnungsfragen - Rechnungen, Versicherung, Zahlung, Mahnprozesse",
                "supervisor": supervisor,
                "package": "practice"
            },
            {
                "name": "practice_document_inbox_agent",
                "description": "Dokumentenverwaltung - Fax/Briefe/Befunde klassifizieren, extrahieren, routen",
                "supervisor": supervisor,
                "package": "practice"
            },
        ]
        
        for agent_info in agents:
            self._register_agent_tool(agent_info)
    
    def _register_general_agents(self):
        """Registriert allgemeine Agents als Tools"""
        agents = [
            {
                "name": "support_triage_agent",
                "description": "Support Triage - allgemeine Support-Anfragen triagieren",
                "supervisor": None,
                "package": "general"
            },
            {
                "name": "support_resolution_agent",
                "description": "Support Resolution - Beschwerden lösen, Probleme beheben",
                "supervisor": "support_triage_agent",
                "package": "general"
            },
        ]
        
        for agent_info in agents:
            self._register_agent_tool(agent_info)
    
    def _register_agent_tool(self, agent_info: Dict[str, Any]):
        """Registriert einen Agent als MCP Tool"""
        agent_name = agent_info["name"]
        
        # Prüfe ob Agent in Registry ist
        if not self.agent_registry.is_registered(agent_name):
            print(f"WARNING: Agent {agent_name} nicht in Registry - überspringe Tool-Registrierung")
            return
        
        # Input Schema für Tool
        input_schema = {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "Benutzer-Nachricht die verarbeitet werden soll"
                },
                "context": {
                    "type": "object",
                    "description": "Zusätzlicher Kontext (Channel, User ID, etc.)",
                    "properties": {
                        "channel": {"type": "string"},
                        "user_id": {"type": "string"},
                        "conversation_id": {"type": "string"}
                    }
                }
            },
            "required": ["user_message"]
        }
        
        tool = MCPToolDefinition(
            name=f"agent_{agent_name}",
            description=agent_info["description"],
            inputSchema=input_schema,
            agent_name=agent_name,
            supervisor=agent_info.get("supervisor"),
            package=agent_info.get("package"),
            category="agent",
            enabled=True
        )
        
        self.tools[tool.name] = tool
    
    def get_tools_for_orchestrator(
        self,
        package_type: Optional[str] = None,
        filtered_agents: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Holt Tools für Orchestrator (MCP-Format)
        
        Args:
            package_type: Filter nach Package Type
            filtered_agents: Gefilterte Agents (vom Intent Agent)
        
        Returns:
            Liste von Tools im MCP-Format
        """
        tools = []
        
        for tool_name, tool_def in self.tools.items():
            # Filter nach Package Type
            if package_type and tool_def.package and tool_def.package != package_type and tool_def.package != "general":
                continue
            
            # Filter nach gefilterten Agents
            if filtered_agents and tool_def.agent_name not in filtered_agents:
                continue
            
            # Nur aktivierte Tools
            if not tool_def.enabled:
                continue
            
            # MCP Tool Format
            mcp_tool = {
                "name": tool_def.name,
                "description": tool_def.description,
                "inputSchema": tool_def.inputSchema,
                "metadata": {
                    "agent_name": tool_def.agent_name,
                    "supervisor": tool_def.supervisor,
                    "package": tool_def.package,
                    "category": tool_def.category
                }
            }
            
            tools.append(mcp_tool)
        
        return tools
    
    def get_tool_by_agent_name(self, agent_name: str) -> Optional[MCPToolDefinition]:
        """Holt Tool Definition für Agent"""
        for tool in self.tools.values():
            if tool.agent_name == agent_name:
                return tool
        return None
    
    def list_all_tools(self) -> List[str]:
        """Listet alle registrierten Tools"""
        return list(self.tools.keys())
    
    def get_supervisor_hierarchy(self) -> Dict[str, List[str]]:
        """
        Holt Supervisor-Hierarchie
        
        Returns:
            Dict mit supervisor -> [agents]
        """
        hierarchy: Dict[str, List[str]] = {}
        
        for tool in self.tools.values():
            if tool.supervisor:
                if tool.supervisor not in hierarchy:
                    hierarchy[tool.supervisor] = []
                hierarchy[tool.supervisor].append(tool.agent_name)
        
        return hierarchy
    
    def verify_supervisor_connections(self) -> Dict[str, Any]:
        """
        Verifiziert Supervisor-Verbindungen
        
        Returns:
            Dict mit Status und fehlenden Verbindungen
        """
        issues = []
        hierarchy = self.get_supervisor_hierarchy()
        
        # Prüfe ob alle Supervisors existieren
        for supervisor, agents in hierarchy.items():
            if not self.agent_registry.is_registered(supervisor):
                issues.append({
                    "type": "missing_supervisor",
                    "supervisor": supervisor,
                    "agents": agents,
                    "message": f"Supervisor {supervisor} nicht in Registry"
                })
        
        # Prüfe ob alle Agents registriert sind
        for tool in self.tools.values():
            if not self.agent_registry.is_registered(tool.agent_name):
                issues.append({
                    "type": "missing_agent",
                    "agent": tool.agent_name,
                    "message": f"Agent {tool.agent_name} nicht in Registry"
                })
        
        return {
            "status": "ok" if not issues else "issues_found",
            "total_tools": len(self.tools),
            "supervisor_hierarchy": hierarchy,
            "issues": issues
        }


# Globale MCP Tool Registry-Instanz
_global_mcp_registry: Optional[MCPToolRegistry] = None


def get_mcp_tool_registry() -> MCPToolRegistry:
    """Holt globale MCP Tool Registry-Instanz"""
    global _global_mcp_registry
    if _global_mcp_registry is None:
        _global_mcp_registry = MCPToolRegistry()
    return _global_mcp_registry
