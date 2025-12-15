"""
Multi-Agent Workflow Beispiel

Zeigt wie mehrere Agents zusammenarbeiten können.
"""

import asyncio
from apps.agents.core.multi_agent_collaboration import (
    get_workflow_orchestrator,
    get_communication_bus
)


async def example_reservation_workflow():
    """
    Beispiel: Reservierungs-Workflow mit mehreren Agents
    
    1. Voice Host Agent nimmt Anfrage entgegen
    2. Integration Agent prüft Verfügbarkeit
    3. CRM Agent erstellt Kontakt
    4. Communications Agent sendet Bestätigung
    """
    orchestrator = get_workflow_orchestrator()
    
    # Erstelle Workflow
    workflow = orchestrator.create_workflow(
        name="Reservierungs-Workflow",
        steps=[
            {
                "step_id": "step1",
                "agent_name": "restaurant_voice_host_agent",
                "action": "handle_reservation_request",
                "input_data": {
                    "user_message": "Ich möchte eine Reservierung für heute Abend, 19:00, 4 Personen"
                }
            },
            {
                "step_id": "step2",
                "agent_name": "integration_agent",
                "action": "check_availability",
                "input_data": {
                    "date": "$memory.step1_date",
                    "time": "$memory.step1_time",
                    "guests": "$memory.step1_guests"
                },
                "dependencies": ["step1"]
            },
            {
                "step_id": "step3",
                "agent_name": "crm_agent",
                "action": "create_contact",
                "input_data": {
                    "name": "$memory.step1_name",
                    "phone": "$memory.step1_phone"
                },
                "dependencies": ["step1"]
            },
            {
                "step_id": "step4",
                "agent_name": "integration_agent",
                "action": "create_reservation",
                "input_data": {
                    "date": "$memory.step1_date",
                    "time": "$memory.step1_time",
                    "guests": "$memory.step1_guests",
                    "contact_id": "$memory.step3_contact_id"
                },
                "dependencies": ["step2", "step3"]
            },
            {
                "step_id": "step5",
                "agent_name": "communications_supervisor",
                "action": "send_confirmation",
                "input_data": {
                    "phone": "$memory.step1_phone",
                    "reservation_id": "$memory.step4_reservation_id"
                },
                "dependencies": ["step4"]
            }
        ]
    )
    
    print(f"Workflow erstellt: {workflow.workflow_id}")
    
    # Führe Workflow aus
    try:
        result = await orchestrator.execute_workflow(workflow.workflow_id)
        print(f"Workflow erfolgreich: {result}")
        return result
    except Exception as e:
        print(f"Workflow fehlgeschlagen: {e}")
        raise


async def example_agent_communication():
    """
    Beispiel: Agent-to-Agent Communication
    
    Voice Host Agent fragt Menu Allergen Agent nach Allergenen.
    """
    bus = get_communication_bus()
    
    # Registriere Handler für Menu Allergen Agent
    async def handle_allergen_query(message):
        """Handler für Allergen-Queries"""
        query = message.payload.get("query")
        # Simuliere Antwort
        return {
            "answer": f"Allergen-Info für: {query}",
            "contains_nuts": False,
            "gluten_free": True
        }
    
    bus.register_handler("restaurant_menu_allergen_agent", handle_allergen_query)
    
    # Voice Host Agent fragt Menu Allergen Agent
    response = await bus.query_agent(
        from_agent="restaurant_voice_host_agent",
        to_agent="restaurant_menu_allergen_agent",
        query="Enthält das Gericht Nüsse?",
        context={"menu_item": "Pasta Carbonara"}
    )
    
    print(f"Response: {response}")
    return response


if __name__ == "__main__":
    print("=" * 80)
    print("MULTI-AGENT COLLABORATION BEISPIELE")
    print("=" * 80)
    print()
    
    # Beispiel 1: Agent Communication
    print("1. Agent-to-Agent Communication:")
    asyncio.run(example_agent_communication())
    print()
    
    # Beispiel 2: Workflow
    print("2. Multi-Agent Workflow:")
    # asyncio.run(example_reservation_workflow())  # Würde echte Agents benötigen
    print("Workflow-Beispiel (benötigt echte Agents)")
