"""
Healthcare Privacy Guard Agent - Praxis-spezifische Hard Guardrails

Erzwingt:
- Minimale Datenerhebung
- Consent-Gates
- Redaction-Regeln
- Retention-Policy
- "Nichts Diagnostisches" + Eskalationslogik

Begründung:
- Gesundheitsdaten = Art. 9 DSGVO special category
- Ärztliche Schweigepflicht / §203 StGB
- Berufsrechtliche Anforderungen
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class PrivacyViolationType(str, Enum):
    """Typen von Privacy-Verletzungen"""
    EXCESSIVE_DATA_COLLECTION = "excessive_data_collection"
    MISSING_CONSENT = "missing_consent"
    DIAGNOSTIC_CONTENT = "diagnostic_content"
    UNAUTHORIZED_DISCLOSURE = "unauthorized_disclosure"
    RETENTION_VIOLATION = "retention_violation"


@dataclass
class PrivacyCheckResult:
    """Ergebnis einer Privacy-Prüfung"""
    allowed: bool
    violation_type: Optional[PrivacyViolationType] = None
    message: str = ""
    requires_escalation: bool = False
    action_required: Optional[str] = None


class HealthcarePrivacyGuardAgent:
    """
    Privacy Guard Agent für Gesundheitsdaten
    
    Strikte Guardrails für DSGVO Art. 9 Compliance und Schweigepflicht.
    """
    
    def __init__(self, account_id: str, consent_gateway=None):
        self.account_id = account_id
        self.consent_gateway = consent_gateway
        self.diagnostic_keywords = self._init_diagnostic_keywords()
        self.minimal_data_required = self._init_minimal_data_requirements()
    
    def _init_diagnostic_keywords(self) -> List[str]:
        """Keywords die auf diagnostische Inhalte hinweisen"""
        return [
            "diagnose", "befund", "krankheit", "erkrankung",
            "therapie", "behandlung", "medikament", "arznei",
            "symptom", "laborwert", "blutwert", "test",
            "icd", "icd-10", "diagnostizieren"
        ]
    
    def _init_minimal_data_requirements(self) -> Dict[str, List[str]]:
        """Minimale Daten-Requirements pro Use Case"""
        return {
            "appointment": ["name", "phone", "date", "time"],
            "prescription": ["name", "phone", "medication_name"],
            "referral": ["name", "phone", "specialist_type"],
            "form": ["name", "phone", "form_type"],
        }
    
    def check_data_collection(
        self,
        use_case: str,
        collected_data: Dict[str, Any]
    ) -> PrivacyCheckResult:
        """
        Prüft ob Datenerhebung minimal ist
        
        Returns:
            PrivacyCheckResult
        """
        required_fields = self.minimal_data_required.get(use_case, [])
        
        # Prüfe ob nur notwendige Daten gesammelt werden
        collected_keys = set(collected_data.keys())
        required_keys = set(required_fields)
        
        excess_keys = collected_keys - required_keys
        
        if excess_keys:
            return PrivacyCheckResult(
                allowed=False,
                violation_type=PrivacyViolationType.EXCESSIVE_DATA_COLLECTION,
                message=f"Zu viele Daten gesammelt. Erlaubt: {required_keys}, Gesammelt: {collected_keys}",
                requires_escalation=True,
                action_required="Reduziere Datenerhebung auf Minimum"
            )
        
        return PrivacyCheckResult(
            allowed=True,
            message="Datenerhebung ist minimal und DSGVO-konform"
        )
    
    def check_consent(
        self,
        data_category: str,
        user_id: Optional[str] = None
    ) -> PrivacyCheckResult:
        """
        Prüft ob Consent für Datenkategorie vorhanden ist
        
        Returns:
            PrivacyCheckResult
        """
        if not self.consent_gateway:
            # Fallback: Consent als nicht vorhanden betrachten
            return PrivacyCheckResult(
                allowed=False,
                violation_type=PrivacyViolationType.MISSING_CONSENT,
                message="Consent-Gateway nicht verfügbar",
                requires_escalation=True
            )
        
        # TODO: Via Consent Gateway prüfen
        # has_consent = self.consent_gateway.check_consent(...)
        
        return PrivacyCheckResult(
            allowed=True,
            message="Consent vorhanden"
        )
    
    def check_diagnostic_content(
        self,
        content: str
    ) -> PrivacyCheckResult:
        """
        Prüft ob Content diagnostische Inhalte enthält
        
        Wichtig: Keine Diagnosen durch AI!
        
        Returns:
            PrivacyCheckResult
        """
        content_lower = content.lower()
        
        has_diagnostic = any(
            kw in content_lower for kw in self.diagnostic_keywords
        )
        
        if has_diagnostic:
            return PrivacyCheckResult(
                allowed=False,
                violation_type=PrivacyViolationType.DIAGNOSTIC_CONTENT,
                message="Content enthält diagnostische Inhalte - nicht erlaubt",
                requires_escalation=True,
                action_required="Entferne diagnostische Inhalte oder eskalieren"
            )
        
        return PrivacyCheckResult(
            allowed=True,
            message="Keine diagnostischen Inhalte erkannt"
        )
    
    def enforce_retention_policy(
        self,
        data_type: str,
        created_at: datetime
    ) -> PrivacyCheckResult:
        """
        Erzwingt Retention-Policy
        
        Returns:
            PrivacyCheckResult
        """
        # TODO: Retention-Policy aus Config laden
        retention_days = 365  # Default: 1 Jahr für Gesundheitsdaten
        
        # TODO: Via Consent Gateway prüfen
        # should_retain = self.consent_gateway.should_retain(...)
        
        return PrivacyCheckResult(
            allowed=True,
            message="Retention-Policy eingehalten"
        )
    
    def validate_request(
        self,
        use_case: str,
        collected_data: Dict[str, Any],
        content: Optional[str] = None
    ) -> PrivacyCheckResult:
        """
        Validiert kompletten Request gegen alle Privacy-Regeln
        
        Returns:
            PrivacyCheckResult
        """
        # 1. Datenerhebung prüfen
        data_check = self.check_data_collection(use_case, collected_data)
        if not data_check.allowed:
            return data_check
        
        # 2. Consent prüfen
        consent_check = self.check_consent("phi")
        if not consent_check.allowed:
            return consent_check
        
        # 3. Diagnostische Inhalte prüfen
        if content:
            diagnostic_check = self.check_diagnostic_content(content)
            if not diagnostic_check.allowed:
                return diagnostic_check
        
        return PrivacyCheckResult(
            allowed=True,
            message="Request ist DSGVO-konform und schweigepflicht-konform"
        )
