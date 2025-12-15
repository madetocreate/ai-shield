"""
Consent and Redaction Gateway - Pipeline-Komponente für PII/PHI-Schutz

Wichtig für DSGVO Art. 9 (Gesundheitsdaten) und allgemeine Datenschutz-Compliance.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta


class DataCategory(str, Enum):
    """Kategorien sensibler Daten"""
    PII = "pii"  # Personenbezogene Daten
    PHI = "phi"  # Protected Health Information
    FINANCIAL = "financial"
    LOCATION = "location"


class ConsentStatus(str, Enum):
    """Consent-Status"""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    EXPIRED = "expired"
    NOT_REQUIRED = "not_required"


@dataclass
class ConsentRecord:
    """Consent-Eintrag"""
    account_id: str
    user_id: Optional[str]
    category: DataCategory
    status: ConsentStatus
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    purpose: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def is_valid(self) -> bool:
        """Prüft ob Consent gültig ist"""
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


@dataclass
class RedactionRule:
    """Redaction-Regel"""
    pattern: str
    replacement: str = "[REDACTED]"
    category: DataCategory = DataCategory.PII
    required_consent: bool = True


class ConsentAndRedactionGateway:
    """
    Gateway für Consent-Management und Daten-Redaction
    
    Pipeline-Komponente die vor Memory/Logs geschaltet wird.
    """
    
    def __init__(self):
        self.consent_records: Dict[str, List[ConsentRecord]] = {}
        self.redaction_rules: List[RedactionRule] = self._default_rules()
        self.retention_policies: Dict[str, int] = {}  # account_id -> days
    
    def _default_rules(self) -> List[RedactionRule]:
        """Standard Redaction-Regeln"""
        return [
            # E-Mail
            RedactionRule(
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                replacement="[EMAIL]",
                category=DataCategory.PII
            ),
            # Telefon (DE Format)
            RedactionRule(
                pattern=r'(\+49|0)[1-9]\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,4}',
                replacement="[PHONE]",
                category=DataCategory.PII
            ),
            # IBAN
            RedactionRule(
                pattern=r'\b[A-Z]{2}\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{0,2}\b',
                replacement="[IBAN]",
                category=DataCategory.FINANCIAL
            ),
            # Kreditkarte
            RedactionRule(
                pattern=r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                replacement="[CARD]",
                category=DataCategory.FINANCIAL
            ),
            # Gesundheitsdaten-Indikatoren (für PHI)
            RedactionRule(
                pattern=r'\b(ICD-10|ICD10|Diagnose|Befund|Laborwert|Medikament|Therapie)\b',
                replacement="[MEDICAL_TERM]",
                category=DataCategory.PHI,
                required_consent=True
            ),
        ]
    
    def check_consent(
        self,
        account_id: str,
        user_id: Optional[str],
        category: DataCategory,
        purpose: Optional[str] = None
    ) -> bool:
        """
        Prüft ob Consent für Datenkategorie vorhanden ist
        
        Returns:
            True wenn Consent vorhanden und gültig
        """
        records = self.consent_records.get(account_id, [])
        
        for record in records:
            if record.category == category and record.is_valid():
                if user_id is None or record.user_id is None or record.user_id == user_id:
                    return True
        
        return False
    
    def grant_consent(
        self,
        account_id: str,
        user_id: Optional[str],
        category: DataCategory,
        expires_in_days: Optional[int] = None,
        purpose: Optional[str] = None
    ) -> ConsentRecord:
        """Erteilt Consent"""
        if account_id not in self.consent_records:
            self.consent_records[account_id] = []
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        record = ConsentRecord(
            account_id=account_id,
            user_id=user_id,
            category=category,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(),
            expires_at=expires_at,
            purpose=purpose
        )
        
        self.consent_records[account_id].append(record)
        return record
    
    def redact_content(
        self,
        content: str,
        account_id: str,
        user_id: Optional[str] = None,
        require_consent: bool = True
    ) -> Tuple[str, List[str]]:
        """
        Redactiert sensible Daten aus Content
        
        Returns:
            Tuple von (redacted_content, redacted_categories)
        """
        redacted = content
        redacted_categories = []
        
        for rule in self.redaction_rules:
            if require_consent and rule.required_consent:
                if not self.check_consent(account_id, user_id, rule.category):
                    # Skip redaction wenn kein Consent
                    continue
            
            matches = re.findall(rule.pattern, redacted, re.IGNORECASE)
            if matches:
                redacted = re.sub(
                    rule.pattern,
                    rule.replacement,
                    redacted,
                    flags=re.IGNORECASE
                )
                if rule.category.value not in redacted_categories:
                    redacted_categories.append(rule.category.value)
        
        return redacted, redacted_categories
    
    def should_retain(
        self,
        account_id: str,
        created_at: datetime
    ) -> bool:
        """
        Prüft ob Daten noch innerhalb Retention-Policy sind
        
        Returns:
            True wenn Daten behalten werden sollen
        """
        retention_days = self.retention_policies.get(account_id)
        if retention_days is None:
            return True  # Keine Retention-Policy = behalten
        
        cutoff = datetime.now() - timedelta(days=retention_days)
        return created_at > cutoff
    
    def set_retention_policy(self, account_id: str, days: int):
        """Setzt Retention-Policy für Account"""
        self.retention_policies[account_id] = days


# Globale Gateway-Instanz
_global_gateway: Optional[ConsentAndRedactionGateway] = None


def get_gateway() -> ConsentAndRedactionGateway:
    """Holt globale Gateway-Instanz"""
    global _global_gateway
    if _global_gateway is None:
        _global_gateway = ConsentAndRedactionGateway()
    return _global_gateway
