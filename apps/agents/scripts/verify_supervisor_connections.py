#!/usr/bin/env python3
"""
Verifiziert Supervisor-Verbindungen und MCP Tool Registrierung

Prüft:
- Alle Agents sind mit Supervisors verbunden
- Alle Agents sind als MCP Tools registriert
- Supervisor-Hierarchie ist korrekt
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.agents.core.mcp_tool_registry import get_mcp_tool_registry
from apps.agents.core.agent_registry import get_registry as get_agent_registry


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("SUPERVISOR & MCP TOOL VERIFICATION")
    print("=" * 60)
    print()
    
    # MCP Tool Registry
    mcp_registry = get_mcp_tool_registry()
    agent_registry = get_agent_registry()
    
    # Verifiziere Supervisor-Verbindungen
    verification = mcp_registry.verify_supervisor_connections()
    
    print("📊 STATISTIKEN")
    print("-" * 60)
    print(f"Total Tools registriert: {verification['total_tools']}")
    print(f"Status: {verification['status']}")
    print()
    
    # Supervisor-Hierarchie
    print("🏗️ SUPERVISOR-HIERARCHIE")
    print("-" * 60)
    hierarchy = verification['supervisor_hierarchy']
    
    if hierarchy:
        for supervisor, agents in hierarchy.items():
            print(f"\n{supervisor}:")
            for agent in agents:
                # Prüfe ob Agent registriert ist
                status = "✅" if agent_registry.is_registered(agent) else "❌"
                print(f"  {status} {agent}")
    else:
        print("Keine Supervisor-Hierarchie gefunden")
    
    print()
    
    # Issues
    if verification['issues']:
        print("⚠️ ISSUES GEFUNDEN")
        print("-" * 60)
        for issue in verification['issues']:
            print(f"\n{issue['type']}:")
            print(f"  {issue['message']}")
            if 'agents' in issue:
                print(f"  Betroffene Agents: {', '.join(issue['agents'])}")
    else:
        print("✅ KEINE ISSUES")
        print("-" * 60)
        print("Alle Supervisor-Verbindungen sind korrekt!")
    
    print()
    
    # Alle Tools auflisten
    print("🛠️ ALLE MCP TOOLS")
    print("-" * 60)
    all_tools = mcp_registry.list_all_tools()
    for tool_name in sorted(all_tools):
        tool_def = mcp_registry.tools.get(tool_name)
        if tool_def:
            supervisor_info = f" → {tool_def.supervisor}" if tool_def.supervisor else " (Supervisor)"
            print(f"  {tool_name} [{tool_def.package}]{supervisor_info}")
    
    print()
    print("=" * 60)
    
    # Exit Code
    sys.exit(0 if verification['status'] == 'ok' else 1)


if __name__ == "__main__":
    main()
