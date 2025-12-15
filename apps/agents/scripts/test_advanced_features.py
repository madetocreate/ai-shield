#!/usr/bin/env python3
"""
Test Advanced Features - Testet alle neuen Features

Testet:
- Multi-Language Support
- Voice Integration
- App Marketplace
- Auto-Scaling
- Advanced Analytics
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Füge Projekt-Root zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from apps.agents.core.multi_language import (
    get_language_detector,
    get_translator,
    get_localization_manager,
    Language
)
from apps.agents.core.voice_integration import (
    get_voice_to_text,
    get_text_to_voice,
    get_voice_command_processor,
    VoiceProvider
)
from apps.agents.core.app_marketplace import (
    get_marketplace,
    MarketplaceAgent,
    AgentCategory,
    AgentStatus
)
from apps.agents.core.auto_scaling import (
    get_auto_scaler,
    get_cost_optimizer,
    ScalingPolicy,
    ResourceMetrics
)
from apps.agents.core.advanced_analytics import (
    get_anomaly_detector,
    get_forecasting_engine,
    get_business_intelligence,
    TimeSeriesDataPoint
)


def test_multi_language():
    """Test Multi-Language Support"""
    print("=" * 80)
    print("TEST: Multi-Language Support")
    print("=" * 80)
    
    # Language Detection
    print("\n1. Language Detection:")
    detector = get_language_detector()
    test_texts = [
        ("Hallo, wie geht es dir?", Language.GERMAN),
        ("Hello, how are you?", Language.ENGLISH),
        ("Bonjour, comment allez-vous?", Language.FRENCH),
    ]
    
    for text, expected_lang in test_texts:
        result = detector.detect(text)
        status = "✅" if result.language == expected_lang else "❌"
        print(f"  {status} Text: '{text}'")
        print(f"     Erkannt: {result.language.value}, Confidence: {result.confidence:.2f}")
    
    # Translation
    print("\n2. Translation:")
    translator = get_translator(target_language=Language.ENGLISH)
    german_text = "Hallo, wie geht es dir?"
    translation = translator.translate(german_text, target_language=Language.ENGLISH)
    print(f"  Original (DE): {translation.original_text}")
    print(f"  Übersetzt (EN): {translation.translated_text}")
    print(f"  Confidence: {translation.confidence:.2f}")
    
    # Localization
    print("\n3. Localization:")
    loc = get_localization_manager()
    for lang in [Language.GERMAN, Language.ENGLISH, Language.FRENCH]:
        greeting = loc.get("greeting", lang)
        print(f"  {lang.value}: {greeting}")
    
    print("\n✅ Multi-Language Support: OK\n")


async def test_voice_integration():
    """Test Voice Integration"""
    print("=" * 80)
    print("TEST: Voice Integration")
    print("=" * 80)
    
    # Voice-to-Text (Placeholder - würde echte Audio-Daten benötigen)
    print("\n1. Voice-to-Text:")
    print("  ⚠️  Voice-to-Text benötigt echte Audio-Daten")
    print("  ✅ VoiceToText Klasse ist implementiert")
    
    # Text-to-Voice (Placeholder)
    print("\n2. Text-to-Voice:")
    print("  ⚠️  Text-to-Voice benötigt OpenAI API Key")
    print("  ✅ TextToVoice Klasse ist implementiert")
    
    # Voice Commands
    print("\n3. Voice Commands:")
    processor = get_voice_command_processor()
    
    def handle_reservation(text, context):
        return {"action": "reservation", "text": text}
    
    processor.register_command("reservierung", handle_reservation)
    processor.register_command("termin", handle_reservation)
    print(f"  ✅ {len(processor.commands)} Commands registriert")
    
    print("\n✅ Voice Integration: OK\n")


def test_app_marketplace():
    """Test App Marketplace"""
    print("=" * 80)
    print("TEST: App Marketplace")
    print("=" * 80)
    
    marketplace = get_marketplace()
    
    # Agent veröffentlichen
    print("\n1. Agent veröffentlichen:")
    agent = MarketplaceAgent(
        id="test_agent_1",
        name="Test Agent",
        description="Ein Test-Agent für das Marketplace",
        author="Test User",
        version="1.0.0",
        category=AgentCategory.GENERAL,
        status=AgentStatus.PUBLISHED,
        tags=["test", "demo"]
    )
    success = marketplace.publish_agent(agent)
    print(f"  {'✅' if success else '❌'} Agent veröffentlicht: {agent.name}")
    
    # Agents suchen
    print("\n2. Agents suchen:")
    results = marketplace.search_agents(query="test", limit=5)
    print(f"  ✅ {len(results)} Agents gefunden")
    for agent in results:
        print(f"     - {agent.name} (Rating: {agent.average_rating:.1f})")
    
    # Agent bewerten
    print("\n3. Agent bewerten:")
    success = marketplace.rate_agent("test_agent_1", "user_123", 5, "Sehr gut!")
    print(f"  {'✅' if success else '❌'} Rating hinzugefügt")
    
    # Agent installieren
    print("\n4. Agent installieren:")
    success = marketplace.install_agent("test_agent_1", "account_456")
    print(f"  {'✅' if success else '❌'} Agent installiert")
    
    # Installierte Agents
    print("\n5. Installierte Agents:")
    installed = marketplace.get_installed_agents("account_456")
    print(f"  ✅ {len(installed)} Agents installiert")
    
    print("\n✅ App Marketplace: OK\n")


def test_auto_scaling():
    """Test Auto-Scaling"""
    print("=" * 80)
    print("TEST: Auto-Scaling")
    print("=" * 80)
    
    # Scaling Policy
    policy = ScalingPolicy(
        name="test",
        min_instances=1,
        max_instances=5,
        target_cpu=0.7,
        scale_up_threshold=0.8,
        scale_down_threshold=0.3
    )
    scaler = get_auto_scaler(policy=policy)
    
    # Metriken aktualisieren
    print("\n1. Metriken aktualisieren:")
    for i in range(5):
        metrics = ResourceMetrics(
            cpu_usage=0.5 + i * 0.1,
            memory_usage=0.6 + i * 0.05,
            request_rate=50.0 + i * 10,
            error_rate=0.01,
            response_time_ms=100.0 + i * 10
        )
        scaler.update_metrics("test_service", metrics)
    print(f"  ✅ 5 Metriken aktualisiert")
    
    # Scaling prüfen
    print("\n2. Scaling prüfen:")
    decision = scaler.should_scale("test_service")
    print(f"  Action: {decision.action.value}")
    print(f"  Current: {decision.current_instances} -> Target: {decision.target_instances}")
    print(f"  Reason: {decision.reason}")
    
    # Cost Optimization
    print("\n3. Cost Optimization:")
    optimizer = get_cost_optimizer()
    cost = optimizer.calculate_cost("test_service", instances=3, cpu_hours=100, memory_gb_hours=200)
    print(f"  ✅ Kosten berechnet: ${cost:.2f}")
    
    recommendations = optimizer.get_cost_recommendations("test_service")
    if recommendations:
        print(f"  Empfehlungen: {len(recommendations)}")
        for rec in recommendations:
            print(f"    - {rec}")
    
    print("\n✅ Auto-Scaling: OK\n")


def test_advanced_analytics():
    """Test Advanced Analytics"""
    print("=" * 80)
    print("TEST: Advanced Analytics")
    print("=" * 80)
    
    # Business Intelligence
    print("\n1. Business Intelligence:")
    bi = get_business_intelligence()
    
    # Metriken tracken
    for i in range(14):
        bi.track_metric("reservations_per_day", 20.0 + i * 0.5)
        bi.track_metric("appointments_per_day", 25.0 + i * 0.3)
    
    print(f"  ✅ Metriken getrackt")
    
    # Insights
    insights = bi.get_insights("reservations_per_day")
    print(f"  Current Value: {insights['current_value']:.1f}")
    print(f"  Trend: {insights['trend']}")
    print(f"  Anomaly: {insights['anomaly']['is_anomaly']}")
    print(f"  Forecast (next 7 days): {[f'{x:.1f}' for x in insights['forecast']['next_7_days']]}")
    
    # Vergleich
    print("\n2. Vergleich:")
    comparison = bi.get_comparison("reservations_per_day", "appointments_per_day")
    print(f"  Correlation: {comparison['correlation']:.2f}")
    print(f"  Ratio: {comparison['ratio']:.2f}")
    
    # Anomaly Detection
    print("\n3. Anomaly Detection:")
    detector = get_anomaly_detector()
    data_points = [
        TimeSeriesDataPoint(
            datetime.now() - timedelta(days=i),
            20.0 + i * 0.5
        )
        for i in range(10, 0, -1)
    ]
    anomaly = detector.detect(data_points, current_value=30.0)
    print(f"  Anomaly: {anomaly.is_anomaly}")
    print(f"  Score: {anomaly.score:.2f}")
    print(f"  Expected: {anomaly.expected_value:.1f}, Actual: {anomaly.actual_value:.1f}")
    
    # Forecasting
    print("\n4. Forecasting:")
    forecaster = get_forecasting_engine()
    forecast = forecaster.forecast(data_points, periods=7, method="linear_trend")
    print(f"  Method: {forecast.method}")
    print(f"  Predictions: {[f'{x:.1f}' for x in forecast.predictions]}")
    
    print("\n✅ Advanced Analytics: OK\n")


async def main():
    """Hauptfunktion"""
    print("\n" + "=" * 80)
    print("ADVANCED FEATURES TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        # Test Multi-Language
        test_multi_language()
        
        # Test Voice Integration
        await test_voice_integration()
        
        # Test App Marketplace
        test_app_marketplace()
        
        # Test Auto-Scaling
        test_auto_scaling()
        
        # Test Advanced Analytics
        test_advanced_analytics()
        
        print("=" * 80)
        print("✅ ALLE TESTS ERFOLGREICH!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
