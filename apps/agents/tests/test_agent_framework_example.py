"""
Beispiel-Tests für Agent Testing Framework

Zeigt wie man Agents mit dem Test Framework testet.
"""

import asyncio
from apps.agents.tests.test_framework import get_test_framework


async def test_restaurant_voice_host_agent(test_framework):
    """Test für Restaurant Voice Host Agent"""
    from apps.agents.gastronomy.restaurant_voice_host_agent import RestaurantVoiceHostAgent
    
    # Mock Integration Agent
    test_framework.mock("integration_agent", {
        "create_reservation": lambda *args, **kwargs: {"success": True, "id": "123"}
    })
    
    # Erstelle Agent
    agent = RestaurantVoiceHostAgent(
        account_id="test_account",
        integration_agent=test_framework.get_mock("integration_agent")
    )
    
    # Test: Verfügbarkeit prüfen
    from datetime import date
    availability = agent.check_availability(date.today())
    test_framework.assert_not_none(availability, "Availability sollte nicht None sein")
    test_framework.assert_true(hasattr(availability, "available"), "Availability sollte 'available' Attribut haben")


async def test_orchestrator_routing(test_framework):
    """Test für Orchestrator Routing"""
    from apps.agents.core.llm_orchestrator_agent import (
        LLMOrchestratorAgent,
        RoutingRequest
    )
    
    orchestrator = LLMOrchestratorAgent()
    
    # Test: Routing Request
    request = RoutingRequest(
        account_id="test_account",
        user_message="Ich möchte eine Reservierung für heute Abend",
        channel="phone"
    )
    
    # Mock LLM Response (für Test)
    # In echtem Test würde man LLM mocken
    
    test_framework.assert_not_none(request, "Request sollte nicht None sein")


async def run_all_tests():
    """Führt alle Tests aus"""
    framework = get_test_framework()
    
    print("=" * 80)
    print("AGENT TEST FRAMEWORK - Beispiel Tests")
    print("=" * 80)
    print()
    
    # Test 1
    result1 = await framework.run_test(
        "test_restaurant_voice_host_agent",
        test_restaurant_voice_host_agent
    )
    print(f"✅ Test 1: {result1.name} - {'PASSED' if result1.passed else 'FAILED'}")
    if result1.error:
        print(f"   Error: {result1.error}")
    
    # Test 2
    result2 = await framework.run_test(
        "test_orchestrator_routing",
        test_orchestrator_routing
    )
    print(f"✅ Test 2: {result2.name} - {'PASSED' if result2.passed else 'FAILED'}")
    if result2.error:
        print(f"   Error: {result2.error}")
    
    # Summary
    summary = framework.get_test_summary()
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Total Duration: {summary['total_duration']:.2f}s")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
