"""
Vertical Package Manifest - Konfigurationssystem für Branchen-Pakete

Ermöglicht austauschbare Paket-Konfigurationen ohne Hardcoding.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class PackageType(str, Enum):
    """Verfügbare Branchen-Pakete"""
    GASTRONOMY = "gastronomy"
    PRACTICE = "practice"


@dataclass
class IntegrationConfig:
    """Konfiguration für eine Integration"""
    integration_id: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyConfig:
    """Policy-Konfiguration für ein Paket"""
    preset: str = "public_website"
    pii_mode: str = "mask"  # mask, block, allow
    require_consent: bool = True
    retention_days: Optional[int] = None
    custom_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerticalPackageManifest:
    """
    Manifest für ein Branchen-Paket
    
    Definiert welche Agents, Integrationen und Policies aktiv sind.
    """
    package_type: PackageType
    account_id: str
    enabled_agents: List[str] = field(default_factory=list)
    integrations: List[IntegrationConfig] = field(default_factory=list)
    policies: PolicyConfig = field(default_factory=PolicyConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VerticalPackageManifest":
        """Lädt Manifest aus Dictionary"""
        package_type = PackageType(data.get("package_type", ""))
        account_id = data.get("account_id", "")
        enabled_agents = data.get("enabled_agents", [])
        
        integrations = [
            IntegrationConfig(**ic) if isinstance(ic, dict) else ic
            for ic in data.get("integrations", [])
        ]
        
        policies_data = data.get("policies", {})
        policies = PolicyConfig(**policies_data) if policies_data else PolicyConfig()
        
        metadata = data.get("metadata", {})
        
        return cls(
            package_type=package_type,
            account_id=account_id,
            enabled_agents=enabled_agents,
            integrations=integrations,
            policies=policies,
            metadata=metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Exportiert Manifest als Dictionary"""
        return {
            "package_type": self.package_type.value,
            "account_id": self.account_id,
            "enabled_agents": self.enabled_agents,
            "integrations": [
                {
                    "integration_id": ic.integration_id,
                    "enabled": ic.enabled,
                    "config": ic.config
                }
                for ic in self.integrations
            ],
            "policies": {
                "preset": self.policies.preset,
                "pii_mode": self.policies.pii_mode,
                "require_consent": self.policies.require_consent,
                "retention_days": self.policies.retention_days,
                "custom_rules": self.policies.custom_rules
            },
            "metadata": self.metadata
        }
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Prüft ob ein Agent aktiviert ist"""
        return agent_name in self.enabled_agents
    
    def get_integration(self, integration_id: str) -> Optional[IntegrationConfig]:
        """Holt Integration-Konfiguration"""
        for ic in self.integrations:
            if ic.integration_id == integration_id and ic.enabled:
                return ic
        return None


class ManifestRegistry:
    """Zentrale Registry für Package Manifests"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("/app/data/manifests")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._manifests: Dict[str, VerticalPackageManifest] = {}
        self._load_all()
    
    def _load_all(self):
        """Lädt alle Manifests aus Storage"""
        if not self.storage_path.exists():
            return
        
        for manifest_file in self.storage_path.glob("*.json"):
            try:
                data = json.loads(manifest_file.read_text())
                manifest = VerticalPackageManifest.from_dict(data)
                self._manifests[manifest.account_id] = manifest
            except Exception as e:
                print(f"Fehler beim Laden von {manifest_file}: {e}")
    
    def get_manifest(self, account_id: str) -> Optional[VerticalPackageManifest]:
        """Holt Manifest für Account"""
        return self._manifests.get(account_id)
    
    def save_manifest(self, manifest: VerticalPackageManifest):
        """Speichert Manifest"""
        self._manifests[manifest.account_id] = manifest
        manifest_file = self.storage_path / f"{manifest.account_id}.json"
        manifest_file.write_text(
            json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False)
        )
    
    def delete_manifest(self, account_id: str):
        """Löscht Manifest"""
        if account_id in self._manifests:
            del self._manifests[account_id]
        manifest_file = self.storage_path / f"{account_id}.json"
        if manifest_file.exists():
            manifest_file.unlink()


# Globale Registry-Instanz
_global_registry: Optional[ManifestRegistry] = None


def get_registry() -> ManifestRegistry:
    """Holt globale Registry-Instanz"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ManifestRegistry()
    return _global_registry
