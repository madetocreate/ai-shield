"""
Configuration Management - Feature Flags, A/B Testing, Dynamische Konfiguration

Features:
- Feature Flags (ein/aus ohne Code-Änderung)
- A/B Testing Framework
- Dynamische Konfiguration (ohne Restart)
- Configuration Versioning
"""

from typing import Dict, Optional, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import logging
import random

logger = logging.getLogger(__name__)


class FeatureFlagStatus(str, Enum):
    """Feature Flag Status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    PERCENTAGE = "percentage"  # Für schrittweise Rollouts


@dataclass
class FeatureFlag:
    """Feature Flag"""
    name: str
    status: FeatureFlagStatus
    percentage: float = 100.0  # 0.0 - 100.0
    enabled_accounts: List[str] = field(default_factory=list)  # Whitelist
    disabled_accounts: List[str] = field(default_factory=list)  # Blacklist
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ABTestVariant:
    """A/B Test Variante"""
    name: str
    weight: float = 50.0  # Prozent (0.0 - 100.0)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTest:
    """A/B Test"""
    name: str
    variants: List[ABTestVariant]
    active: bool = True
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    metrics: List[str] = field(default_factory=list)  # Metriken zum Tracken
    winner: Optional[str] = None  # Gewinner-Variante


class ConfigurationManager:
    """
    Configuration Manager
    
    Verwaltet Feature Flags, A/B Tests und dynamische Konfiguration.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialisiert Configuration Manager
        
        Args:
            storage_path: Pfad für Storage (JSON-Datei)
        """
        self.storage_path = storage_path or os.getenv(
            "CONFIG_STORAGE_PATH",
            "data/configuration.json"
        )
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.configurations: Dict[str, Dict[str, Any]] = {}
        self._load_data()
    
    def _load_data(self):
        """Lädt Daten aus Storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Lade Feature Flags
                    for flag_data in data.get("feature_flags", []):
                        flag = FeatureFlag(
                            name=flag_data["name"],
                            status=FeatureFlagStatus(flag_data["status"]),
                            percentage=flag_data.get("percentage", 100.0),
                            enabled_accounts=flag_data.get("enabled_accounts", []),
                            disabled_accounts=flag_data.get("disabled_accounts", []),
                            metadata=flag_data.get("metadata", {}),
                            created_at=datetime.fromisoformat(flag_data.get("created_at", datetime.now().isoformat())),
                            updated_at=datetime.fromisoformat(flag_data.get("updated_at", datetime.now().isoformat()))
                        )
                        self.feature_flags[flag.name] = flag
                    
                    # Lade A/B Tests
                    for test_data in data.get("ab_tests", []):
                        variants = [
                            ABTestVariant(
                                name=v["name"],
                                weight=v.get("weight", 50.0),
                                config=v.get("config", {})
                            )
                            for v in test_data.get("variants", [])
                        ]
                        test = ABTest(
                            name=test_data["name"],
                            variants=variants,
                            active=test_data.get("active", True),
                            start_date=datetime.fromisoformat(test_data.get("start_date", datetime.now().isoformat())),
                            end_date=datetime.fromisoformat(test_data["end_date"]) if test_data.get("end_date") else None,
                            metrics=test_data.get("metrics", []),
                            winner=test_data.get("winner")
                        )
                        self.ab_tests[test.name] = test
                    
                    # Lade Configurations
                    self.configurations = data.get("configurations", {})
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Konfiguration: {e}")
    
    def _save_data(self):
        """Speichert Daten in Storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "feature_flags": [
                    {
                        "name": flag.name,
                        "status": flag.status.value,
                        "percentage": flag.percentage,
                        "enabled_accounts": flag.enabled_accounts,
                        "disabled_accounts": flag.disabled_accounts,
                        "metadata": flag.metadata,
                        "created_at": flag.created_at.isoformat(),
                        "updated_at": flag.updated_at.isoformat()
                    }
                    for flag in self.feature_flags.values()
                ],
                "ab_tests": [
                    {
                        "name": test.name,
                        "variants": [
                            {
                                "name": v.name,
                                "weight": v.weight,
                                "config": v.config
                            }
                            for v in test.variants
                        ],
                        "active": test.active,
                        "start_date": test.start_date.isoformat(),
                        "end_date": test.end_date.isoformat() if test.end_date else None,
                        "metrics": test.metrics,
                        "winner": test.winner
                    }
                    for test in self.ab_tests.values()
                ],
                "configurations": self.configurations
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
    
    # Feature Flags
    def create_feature_flag(
        self,
        name: str,
        status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
        percentage: float = 100.0
    ) -> FeatureFlag:
        """Erstellt Feature Flag"""
        flag = FeatureFlag(
            name=name,
            status=status,
            percentage=percentage
        )
        self.feature_flags[name] = flag
        self._save_data()
        logger.info(f"Feature Flag erstellt: {name}")
        return flag
    
    def is_feature_enabled(
        self,
        feature_name: str,
        account_id: Optional[str] = None
    ) -> bool:
        """
        Prüft ob Feature aktiviert ist
        
        Args:
            feature_name: Feature Name
            account_id: Account ID (optional, für Account-spezifische Flags)
        
        Returns:
            True wenn aktiviert
        """
        if feature_name not in self.feature_flags:
            return False
        
        flag = self.feature_flags[feature_name]
        
        # Blacklist prüfen
        if account_id and account_id in flag.disabled_accounts:
            return False
        
        # Whitelist prüfen
        if account_id and account_id in flag.enabled_accounts:
            return True
        
        # Status prüfen
        if flag.status == FeatureFlagStatus.DISABLED:
            return False
        
        if flag.status == FeatureFlagStatus.ENABLED:
            return True
        
        if flag.status == FeatureFlagStatus.PERCENTAGE:
            # Prozent-basierte Rollout
            if account_id:
                # Deterministic basierend auf Account ID
                hash_value = hash(f"{feature_name}:{account_id}") % 100
                return hash_value < flag.percentage
            else:
                # Random
                return random.random() * 100 < flag.percentage
        
        return False
    
    def enable_feature(self, feature_name: str, percentage: float = 100.0):
        """Aktiviert Feature"""
        if feature_name not in self.feature_flags:
            self.create_feature_flag(feature_name, FeatureFlagStatus.ENABLED, percentage)
        else:
            flag = self.feature_flags[feature_name]
            flag.status = FeatureFlagStatus.ENABLED if percentage == 100.0 else FeatureFlagStatus.PERCENTAGE
            flag.percentage = percentage
            flag.updated_at = datetime.now()
            self._save_data()
    
    def disable_feature(self, feature_name: str):
        """Deaktiviert Feature"""
        if feature_name in self.feature_flags:
            flag = self.feature_flags[feature_name]
            flag.status = FeatureFlagStatus.DISABLED
            flag.updated_at = datetime.now()
            self._save_data()
    
    # A/B Testing
    def create_ab_test(
        self,
        name: str,
        variants: List[ABTestVariant],
        metrics: List[str] = None
    ) -> ABTest:
        """Erstellt A/B Test"""
        # Normalisiere Gewichte
        total_weight = sum(v.weight for v in variants)
        if total_weight != 100.0:
            for variant in variants:
                variant.weight = (variant.weight / total_weight) * 100.0
        
        test = ABTest(
            name=name,
            variants=variants,
            metrics=metrics or []
        )
        self.ab_tests[name] = test
        self._save_data()
        logger.info(f"A/B Test erstellt: {name}")
        return test
    
    def get_ab_test_variant(
        self,
        test_name: str,
        account_id: Optional[str] = None
    ) -> Optional[ABTestVariant]:
        """
        Holt Variante für A/B Test (deterministic basierend auf Account ID)
        
        Args:
            test_name: Test Name
            account_id: Account ID (optional)
        
        Returns:
            ABTestVariant oder None
        """
        if test_name not in self.ab_tests:
            return None
        
        test = self.ab_tests[test_name]
        if not test.active:
            return None
        
        # Deterministic Assignment basierend auf Account ID
        if account_id:
            hash_value = hash(f"{test_name}:{account_id}") % 100
            cumulative = 0.0
            for variant in test.variants:
                cumulative += variant.weight
                if hash_value < cumulative:
                    return variant
        else:
            # Random Assignment
            rand = random.random() * 100
            cumulative = 0.0
            for variant in test.variants:
                cumulative += variant.weight
                if rand < cumulative:
                    return variant
        
        return test.variants[0] if test.variants else None
    
    def end_ab_test(self, test_name: str, winner: Optional[str] = None):
        """Beendet A/B Test"""
        if test_name in self.ab_tests:
            test = self.ab_tests[test_name]
            test.active = False
            test.end_date = datetime.now()
            test.winner = winner
            self._save_data()
    
    # Dynamische Konfiguration
    def set_config(self, key: str, value: Any, namespace: str = "default"):
        """Setzt Konfiguration"""
        if namespace not in self.configurations:
            self.configurations[namespace] = {}
        self.configurations[namespace][key] = value
        self._save_data()
    
    def get_config(self, key: str, default: Any = None, namespace: str = "default") -> Any:
        """Holt Konfiguration"""
        if namespace in self.configurations:
            return self.configurations[namespace].get(key, default)
        return default
    
    def get_all_configs(self, namespace: str = "default") -> Dict[str, Any]:
        """Holt alle Konfigurationen eines Namespaces"""
        return self.configurations.get(namespace, {})


# Globale Configuration Manager-Instanz
_global_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Holt globale Configuration Manager-Instanz"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
    return _global_config_manager
