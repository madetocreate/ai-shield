"""
Tests für Praxis-Agents
"""

import pytest
from datetime import date, time, datetime
from apps.agents.practice import (
    PracticeSupervisorAgent,
    PracticePhoneReceptionAgent,
    PracticeAppointmentReminderAgent,
    PracticePatientIntakeFormsAgent,
    PracticeAdminRequestsAgent,
    HealthcarePrivacyGuardAgent,
)
from apps.agents.practice.practice_supervisor_agent import PracticeIntent


class TestPracticeSupervisorAgent:
    """Tests für Practice Supervisor Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = PracticeSupervisorAgent(account_id="test-praxis")
        assert agent.account_id == "test-praxis"
        assert len(agent.intent_keywords) > 0
        assert len(agent.safety_keywords) > 0
    
    def test_appointment_intent(self):
        """Test Termin-Intent-Erkennung"""
        agent = PracticeSupervisorAgent(account_id="test-praxis")
        decision = agent.route_request("Ich möchte einen Termin vereinbaren")
        
        assert decision.intent == PracticeIntent.APPOINTMENT
        assert decision.target_agent == "practice_phone_reception_agent"
        assert decision.confidence > 0
    
    def test_symptom_intent_with_safety(self):
        """Test Symptom-Intent mit Safety-Check"""
        agent = PracticeSupervisorAgent(account_id="test-praxis")
        decision = agent.route_request("Ich habe starke Schmerzen")
        
        assert decision.intent == PracticeIntent.SYMPTOM_QUERY
        assert decision.requires_safety_check is True
    
    def test_prescription_intent(self):
        """Test Rezept-Intent-Erkennung"""
        agent = PracticeSupervisorAgent(account_id="test-praxis")
        decision = agent.route_request("Ich brauche ein Rezept")
        
        assert decision.intent == PracticeIntent.PRESCRIPTION_REQUEST
        assert decision.target_agent == "practice_admin_requests_agent"
    
    def test_practice_context(self):
        """Test Praxis-Kontext-Erkennung"""
        agent = PracticeSupervisorAgent(account_id="test-praxis")
        assert agent.is_practice_context("Ich brauche einen Arzttermin")
        assert not agent.is_practice_context("Ich möchte im Restaurant essen")


class TestPracticePhoneReceptionAgent:
    """Tests für Practice Phone Reception Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = PracticePhoneReceptionAgent(account_id="test-praxis")
        assert agent.account_id == "test-praxis"
        assert "opening_hours" in agent.practice_info
    
    def test_get_opening_hours(self):
        """Test Öffnungszeiten-Abfrage"""
        agent = PracticePhoneReceptionAgent(account_id="test-praxis")
        hours = agent.get_opening_hours("monday")
        assert len(hours) > 0
    
    def test_safety_routing_emergency(self):
        """Test Safety-Routing bei Notfall"""
        agent = PracticePhoneReceptionAgent(account_id="test-praxis")
        result = agent.handle_safety_routing("Ich habe starke Brustschmerzen")
        
        assert result["action"] == "emergency"
        assert result["requires_escalation"] is True
        assert result["priority"] == "critical"
    
    def test_safety_routing_normal(self):
        """Test Safety-Routing bei normalen Symptomen"""
        agent = PracticePhoneReceptionAgent(account_id="test-praxis")
        result = agent.handle_safety_routing("Ich habe leichte Kopfschmerzen")
        
        assert result["action"] == "appointment_offer"
        assert result["requires_escalation"] is False


class TestPracticeAppointmentReminderAgent:
    """Tests für Practice Appointment Reminder Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = PracticeAppointmentReminderAgent(account_id="test-praxis")
        assert agent.account_id == "test-praxis"
    
    def test_schedule_reminder(self):
        """Test Reminder planen"""
        agent = PracticeAppointmentReminderAgent(account_id="test-praxis")
        appointment_date = datetime.now().replace(hour=10, minute=0)
        
        reminder = agent.schedule_reminder(
            appointment_id="APT-123",
            appointment_date=appointment_date,
            patient_name="Max Mustermann",
            phone="0123456789",
            days_before=1
        )
        
        assert reminder.appointment_id == "APT-123"
        assert reminder.patient_name == "Max Mustermann"
        assert reminder.status.value == "pending"
    
    def test_process_confirmation_yes(self):
        """Test Bestätigung verarbeiten (JA)"""
        agent = PracticeAppointmentReminderAgent(account_id="test-praxis")
        # Mock Reminder würde hier hinzugefügt werden


class TestPracticePatientIntakeFormsAgent:
    """Tests für Practice Patient Intake Forms Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = PracticePatientIntakeFormsAgent(account_id="test-praxis")
        assert agent.account_id == "test-praxis"
    
    def test_create_form_request(self):
        """Test Formular-Anfrage erstellen"""
        agent = PracticePatientIntakeFormsAgent(account_id="test-praxis")
        # Mock würde hier hinzugefügt werden


class TestPracticeAdminRequestsAgent:
    """Tests für Practice Admin Requests Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = PracticeAdminRequestsAgent(account_id="test-praxis")
        assert agent.account_id == "test-praxis"
    
    def test_detect_prescription_request(self):
        """Test Rezept-Anfrage erkennen"""
        agent = PracticeAdminRequestsAgent(account_id="test-praxis")
        request_type = agent._detect_request_type("Ich brauche ein Rezept")
        
        assert request_type.value == "prescription"
    
    def test_detect_referral_request(self):
        """Test Überweisungs-Anfrage erkennen"""
        agent = PracticeAdminRequestsAgent(account_id="test-praxis")
        request_type = agent._detect_request_type("Ich brauche eine Überweisung")
        
        assert request_type.value == "referral"


class TestHealthcarePrivacyGuardAgent:
    """Tests für Healthcare Privacy Guard Agent"""
    
    def test_init(self):
        """Test Agent-Initialisierung"""
        agent = HealthcarePrivacyGuardAgent(account_id="test-praxis")
        assert agent.account_id == "test-praxis"
        assert len(agent.diagnostic_keywords) > 0
    
    def test_check_diagnostic_content(self):
        """Test diagnostische Inhalte erkennen"""
        agent = HealthcarePrivacyGuardAgent(account_id="test-praxis")
        result = agent.check_diagnostic_content("Die Diagnose ist Diabetes")
        
        assert result.allowed is False
        assert result.violation_type.value == "diagnostic_content"
        assert result.requires_escalation is True
    
    def test_check_data_collection(self):
        """Test Datenerhebung prüfen"""
        agent = HealthcarePrivacyGuardAgent(account_id="test-praxis")
        result = agent.check_data_collection(
            use_case="appointment",
            collected_data={
                "name": "Max Mustermann",
                "phone": "0123456789",
                "date": "2024-01-15",
                "time": "10:00"
            }
        )
        
        # Sollte erlaubt sein (nur notwendige Daten)
        assert result.allowed is True
    
    def test_validate_request(self):
        """Test Request validieren"""
        agent = HealthcarePrivacyGuardAgent(account_id="test-praxis")
        validation = agent.validate_request(
            use_case="appointment",
            collected_data={
                "name": "Max Mustermann",
                "phone": "0123456789"
            },
            content="Ich möchte einen Termin"
        )
        
        # Sollte valid sein
        assert validation.allowed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
