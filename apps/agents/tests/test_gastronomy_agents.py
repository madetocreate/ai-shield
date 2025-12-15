"""
Tests für Gastronomie-Agents
"""

import pytest
from datetime import date, time, datetime
from apps.agents.gastronomy import (
    GastronomySupervisorAgent,
    RestaurantVoiceHostAgent,
    RestaurantMenuAllergenAgent,
    RestaurantTakeoutOrderAgent,
    RestaurantReputationAgent,
    RestaurantEventsCateringAgent,
)
from apps.agents.gastronomy.gastronomy_supervisor_agent import GastronomyIntent


class TestGastronomySupervisorAgent:
    """Tests für Gastronomy Supervisor Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = GastronomySupervisorAgent(account_id="test-restaurant")
        assert agent.account_id == "test-restaurant"
        assert len(agent.intent_keywords) > 0
    
    def test_reservation_intent(self):
        """Test Reservierungs-Intent-Erkennung"""
        agent = GastronomySupervisorAgent(account_id="test-restaurant")
        decision = agent.route_request("Ich möchte einen Tisch für morgen reservieren")
        
        assert decision.intent == GastronomyIntent.RESERVATION
        assert decision.target_agent == "restaurant_voice_host_agent"
        assert decision.confidence > 0
    
    def test_takeout_intent(self):
        """Test Takeout-Intent-Erkennung"""
        agent = GastronomySupervisorAgent(account_id="test-restaurant")
        decision = agent.route_request("Ich möchte bestellen zum Mitnehmen")
        
        assert decision.intent == GastronomyIntent.TAKEOUT_ORDER
        assert decision.target_agent == "restaurant_takeout_order_agent"
    
    def test_allergen_intent(self):
        """Test Allergen-Intent-Erkennung"""
        agent = GastronomySupervisorAgent(account_id="test-restaurant")
        decision = agent.route_request("Ist das Gericht glutenfrei?")
        
        assert decision.intent == GastronomyIntent.ALLERGEN_QUERY
        assert decision.target_agent == "restaurant_menu_allergen_agent"
    
    def test_event_intent(self):
        """Test Event-Intent-Erkennung"""
        agent = GastronomySupervisorAgent(account_id="test-restaurant")
        decision = agent.route_request("Wir brauchen Catering für 20 Personen")
        
        assert decision.intent == GastronomyIntent.EVENT_CATERING
        assert decision.target_agent == "restaurant_events_catering_agent"
    
    def test_gastronomy_context(self):
        """Test Gastro-Kontext-Erkennung"""
        agent = GastronomySupervisorAgent(account_id="test-restaurant")
        assert agent.is_gastronomy_context("Ich möchte im Restaurant essen")
        assert not agent.is_gastronomy_context("Ich brauche einen Arzttermin")


class TestRestaurantVoiceHostAgent:
    """Tests für Restaurant Voice Host Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = RestaurantVoiceHostAgent(account_id="test-restaurant")
        assert agent.account_id == "test-restaurant"
        assert "opening_hours" in agent.restaurant_info
    
    def test_get_opening_hours(self):
        """Test Öffnungszeiten-Abfrage"""
        agent = RestaurantVoiceHostAgent(account_id="test-restaurant")
        hours = agent.get_opening_hours("monday")
        assert "monday" in hours.lower() or "montag" in hours.lower()
    
    def test_get_address_info(self):
        """Test Adress-Info"""
        agent = RestaurantVoiceHostAgent(account_id="test-restaurant")
        address = agent.get_address_info()
        assert len(address) > 0
    
    def test_handle_general_query(self):
        """Test allgemeine Anfragen"""
        agent = RestaurantVoiceHostAgent(account_id="test-restaurant")
        response = agent.handle_general_query("Wann habt ihr geöffnet?")
        assert len(response) > 0


class TestRestaurantMenuAllergenAgent:
    """Tests für Restaurant Menu Allergen Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = RestaurantMenuAllergenAgent(account_id="test-restaurant")
        assert agent.account_id == "test-restaurant"
    
    def test_check_allergen_unknown_dish(self):
        """Test Allergen-Check für unbekanntes Gericht"""
        agent = RestaurantMenuAllergenAgent(account_id="test-restaurant")
        result = agent.check_allergen("Unbekanntes Gericht", "gluten")
        
        assert result["contains"] is None
        assert result["may_contain_traces"] is True
        assert result["requires_staff_notification"] is True
    
    def test_format_allergen_response(self):
        """Test Allergen-Antwort-Formatierung"""
        agent = RestaurantMenuAllergenAgent(account_id="test-restaurant")
        # Test mit Mock-Daten würde hier hinzugefügt werden


class TestRestaurantTakeoutOrderAgent:
    """Tests für Restaurant Takeout Order Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = RestaurantTakeoutOrderAgent(account_id="test-restaurant")
        assert agent.account_id == "test-restaurant"
    
    def test_start_order(self):
        """Test Bestellung starten"""
        agent = RestaurantTakeoutOrderAgent(account_id="test-restaurant")
        order = agent.start_order("Max Mustermann", "0123456789")
        
        assert order.customer_name == "Max Mustermann"
        assert order.phone == "0123456789"
        assert len(order.items) == 0
        assert order.status == "pending"
    
    def test_add_item(self):
        """Test Position hinzufügen"""
        agent = RestaurantTakeoutOrderAgent(account_id="test-restaurant")
        order = agent.start_order("Max Mustermann", "0123456789")
        item = agent.add_item(order, "Pizza Margherita", quantity=2)
        
        assert item.dish_name == "Pizza Margherita"
        assert item.quantity == 2
        assert len(order.items) == 1


class TestRestaurantReputationAgent:
    """Tests für Restaurant Reputation Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = RestaurantReputationAgent(account_id="test-restaurant")
        assert agent.account_id == "test-restaurant"
    
    def test_analyze_review_positive(self):
        """Test positive Review-Analyse"""
        agent = RestaurantReputationAgent(account_id="test-restaurant")
        sentiment = agent.analyze_review("Sehr lecker, gerne wieder!", 5)
        
        assert sentiment.value == "positive"
    
    def test_analyze_review_negative(self):
        """Test negative Review-Analyse"""
        agent = RestaurantReputationAgent(account_id="test-restaurant")
        sentiment = agent.analyze_review("Schlecht, nie wieder!", 1)
        
        assert sentiment.value in ["negative", "critical"]
    
    def test_generate_positive_response(self):
        """Test positive Antwort-Generierung"""
        agent = RestaurantReputationAgent(account_id="test-restaurant")
        # Mock Review würde hier hinzugefügt werden


class TestRestaurantEventsCateringAgent:
    """Tests für Restaurant Events Catering Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = RestaurantEventsCateringAgent(account_id="test-restaurant")
        assert agent.account_id == "test-restaurant"
    
    def test_create_event_request(self):
        """Test Event-Anfrage erstellen"""
        agent = RestaurantEventsCateringAgent(account_id="test-restaurant")
        request = agent.create_event_request("Catering für 20 Personen")
        
        assert request.event_id.startswith("EVT-")
        assert request.status == "inquiry"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
