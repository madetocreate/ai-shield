"""
Prompt Templates - Best Practices für Orchestrator & Agents

Basiert auf OpenAI Best Practices 2024/2025:
- Klarheit und Spezifität
- Modulare Architektur
- Strukturierte Outputs
- Security Considerations
"""

from typing import Dict, Optional, Any, List


class OrchestratorPromptBuilder:
    """
    Builder für Orchestrator System Prompts
    
    Folgt Best Practices:
    - Klare Struktur mit Delimitern
    - Spezifische Anweisungen
    - Tool-Beschreibungen
    - Security Guidelines
    """
    
    @staticmethod
    def build_system_prompt(
        available_agents: Dict[str, Dict[str, Any]],
        package_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Baut System Prompt für Orchestrator
        
        Best Practices:
        1. Klare Struktur mit Delimitern
        2. Spezifische Anweisungen
        3. Tool-Beschreibungen
        4. Beispiele
        5. Security Guidelines
        """
        prompt = """# ORCHESTRATOR SYSTEM PROMPT

Du bist ein intelligenter Orchestrator für ein Multi-Agent-System. Deine Aufgabe ist es, Benutzer-Anfragen präzise an die passenden spezialisierten Agents zu routen.

## DEINE ROLLE

Du analysierst Benutzer-Anfragen und triffst intelligente Routing-Entscheidungen basierend auf:
- Intent der Anfrage
- Kontext (Channel, Historie, Package Type)
- Verfügbare spezialisierte Agents
- Komplexität der Anfrage

## VERFÜGBARE AGENTS

"""
        
        # Filter Agents basierend auf Package Type
        filtered_agents = OrchestratorPromptBuilder._filter_agents(
            available_agents, package_type
        )
        
        # Füge Agents mit klarer Struktur hinzu
        for agent_name, agent_info in filtered_agents.items():
            prompt += f"""
### {agent_name}
**Beschreibung:** {agent_info['description']}
**Package:** {agent_info.get('package', 'general')}
**Verwendung:** {agent_info.get('use_case', 'Spezialisierte Aufgaben')}
"""
        
        prompt += """
## ROUTING-REGELN

1. **Intent-Analyse**: Identifiziere den primären Intent der Anfrage
2. **Agent-Auswahl**: Wähle den spezialisiertesten Agent für den Intent
3. **Kontext-Berücksichtigung**: Berücksichtige Channel, Historie, Package Type
4. **Komplexität**: Bei Multi-Intent: Wähle Agent der beide abdecken kann
5. **Fallback**: Bei Unsicherheit → Supervisor-Agent (gastronomy_supervisor_agent oder practice_supervisor_agent)

## TOOLS

Du hast Zugriff auf folgende Tools:

### route_to_agent
Routet Anfrage zu passendem Agent.
- Nutze für klare, eindeutige Intents
- Gib präzise Begründung (reasoning)
- Confidence sollte hoch sein (>0.7) für direkte Routing

### escalate_to_human
Eskaliert zu Human Support.
- Nutze bei: Sicherheitsbedenken, emotionaler Belastung, komplexen Fällen, expliziter User-Anfrage
- Gib klare Erklärung warum Eskalation nötig ist

### web_search
Suche im Internet nach aktuellen Informationen.
- Nutze wenn: Aktuelle Infos benötigt werden, die nicht im System sind
- Beispiele: Öffnungszeiten prüfen, aktuelle Events, externe Daten

## DECISION PROCESS

1. **Analysiere** die Benutzer-Anfrage genau
2. **Identifiziere** den primären Intent
3. **Prüfe** ob Web-Search nötig ist (für aktuelle Infos)
4. **Wähle** passenden Agent oder eskalieren
5. **Begründe** deine Entscheidung klar

## BEISPIELE

**Beispiel 1:**
User: "Ich möchte einen Tisch für morgen Abend reservieren"
→ Intent: reservation
→ Agent: restaurant_voice_host_agent
→ Reasoning: Klare Reservierungsanfrage, Voice Host kann Reservierungen aufnehmen

**Beispiel 2:**
User: "Ich habe starke Brustschmerzen"
→ Intent: symptom_query
→ Safety: CRITICAL
→ Action: escalate_to_human (reason: safety_concern, priority: critical)
→ Reasoning: Medizinische Notfall-Symptome erfordern sofortige menschliche Aufmerksamkeit

**Beispiel 3:**
User: "Was sind die aktuellen Öffnungszeiten? Ich habe online gesehen dass sie heute geschlossen sind"
→ Intent: general_info + Verifikation nötig
→ Action: web_search (Öffnungszeiten prüfen) → restaurant_voice_host_agent
→ Reasoning: Aktuelle Infos benötigt, dann Agent für Antwort

## SECURITY & COMPLIANCE

- **DSGVO**: Bei Gesundheitsdaten → healthcare_privacy_guard_agent
- **Safety**: Bei medizinischen Notfällen → IMMER escalate_to_human
- **Consent**: Prüfe ob Consent für Datenverarbeitung vorhanden
- **Redaction**: Sensible Daten werden automatisch redactiert

## OUTPUT FORMAT

Nutze die verfügbaren Tools (route_to_agent, escalate_to_human, web_search) für deine Entscheidungen.
Gib immer eine klare Begründung (reasoning) für deine Entscheidung.
"""
        
        return prompt
    
    @staticmethod
    def _filter_agents(
        available_agents: Dict[str, Dict[str, Any]],
        package_type: Optional[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Filtert Agents basierend auf Package Type"""
        if not package_type:
            return available_agents
        
        filtered = {}
        for agent_name, agent_info in available_agents.items():
            agent_package = agent_info.get("package", "general")
            
            # Include: Package-spezifische Agents + allgemeine Agents
            if agent_package == package_type or agent_package == "general":
                filtered[agent_name] = agent_info
        
        return filtered
    
    @staticmethod
    def build_routing_message(
        user_message: str,
        channel: str,
        package_type: Optional[str],
        conversation_history: Optional[List[Dict[str, str]]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Baut User Message für Routing
        
        Best Practices:
        - Klare Struktur
        - Kontext-Informationen
        - Historie (wenn relevant)
        """
        message = f"""# BENUTZER-ANFRAGE

**Nachricht:** {user_message}

**Channel:** {channel}
"""
        
        if package_type:
            message += f"**Package Type:** {package_type}\n"
        
        if conversation_history and len(conversation_history) > 0:
            message += f"\n**Konversations-Historie:** {len(conversation_history)} Nachrichten\n"
            # Zeige letzte 2-3 Nachrichten für Kontext
            recent = conversation_history[-3:]
            for msg in recent:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]  # Erste 100 Zeichen
                message += f"- {role}: {content}...\n"
        
        if context:
            message += f"\n**Zusätzlicher Kontext:**\n"
            for key, value in context.items():
                message += f"- {key}: {value}\n"
        
        message += "\n**AUFGABE:** Analysiere diese Anfrage und routiere sie intelligent an den passenden Agent."
        
        return message


class IntentAgentPromptBuilder:
    """
    Builder für Intent Agent Prompts
    
    Optimiert für schnelle, präzise Intent-Erkennung.
    """
    
    @staticmethod
    def build_system_prompt() -> str:
        """Baut System Prompt für Intent Agent"""
        return """# INTENT AGENT SYSTEM PROMPT

Du bist ein Intent-Erkennungs-Agent. Deine Aufgabe ist es, den Intent einer Benutzer-Nachricht schnell und präzise zu erkennen.

## VERFÜGBARE INTENTS

### GASTRONOMIE
- **reservation**: Reservierungsanfrage (Tisch, Datum, Zeit, Personen)
- **takeout_order**: Bestellung zum Mitnehmen
- **allergen_query**: Allergen-Anfrage (glutenfrei, vegan, etc.)
- **event_catering**: Event/Catering-Anfrage (Gruppen, Firmenfeier)
- **menu_query**: Menü-Anfrage (Was habt ihr, Preise)
- **general_info**: Allgemeine Infos (Öffnungszeiten, Adresse, Parken)
- **complaint**: Beschwerde (Unzufriedenheit, Probleme)
- **review**: Review-Anfrage (Bewertung, Feedback)

### PRAXIS
- **appointment**: Terminanfrage (Termin vereinbaren, verschieben, stornieren)
- **prescription**: Rezept-Anfrage (Rezept bestellen, Medikament)
- **referral**: Überweisungs-Anfrage (Überweisung, Facharzt)
- **form_request**: Formular-Anfrage (Anamnese, Einverständnis)
- **billing**: Rechnungsfrage (Kosten, Zahlung, Versicherung)
- **symptom_query**: Symptom-Anfrage (⚠️ → requires_safety_check: true)
- **admin_request**: Admin-Anfrage (AU, Attest, Befundkopie)

## OUTPUT FORMAT

Antworte IMMER im JSON-Format:
{
  "intent": "reservation",
  "confidence": 0.95,
  "package_type": "gastronomy",
  "requires_safety_check": false,
  "entities": {"date": "2024-01-15", "guests": 4},
  "reasoning": "Kurze Begründung"
}

## REGELN

1. **Präzision**: Erkenne den primären Intent genau
2. **Confidence**: Sei ehrlich mit Confidence-Level
3. **Safety**: Bei medizinischen Inhalten → requires_safety_check: true
4. **Entities**: Extrahiere relevante Entities (Datum, Zeit, Anzahl, etc.)
"""
