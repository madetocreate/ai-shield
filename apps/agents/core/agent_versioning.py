"""
Agent Versioning - Semantic Versioning, Version History, Rollback

Features:
- Semantic Versioning für Agents
- Version History
- Rollback zu älteren Versionen
- Version Comparison
- Migration Tools
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import logging
import re

logger = logging.getLogger(__name__)


class VersionType(str, Enum):
    """Version Type"""
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, backward compatible


@dataclass
class AgentVersion:
    """Agent Version"""
    agent_name: str
    version: str  # Semantic Version (e.g., "1.2.3")
    version_type: VersionType
    code: str  # Agent Code
    description: str
    changelog: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)  # agent_name -> version
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    is_active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentVersionManager:
    """
    Agent Version Manager
    
    Verwaltet Versionen von Agents.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialisiert Version Manager
        
        Args:
            storage_path: Pfad für Storage
        """
        self.storage_path = storage_path or os.getenv(
            "VERSION_STORAGE_PATH",
            "data/agent_versions.json"
        )
        self.versions: Dict[str, Dict[str, AgentVersion]] = {}  # agent_name -> {version -> AgentVersion}
        self.active_versions: Dict[str, str] = {}  # agent_name -> active_version
        self._load_data()
    
    def _load_data(self):
        """Lädt Daten aus Storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for agent_name, versions_data in data.get("versions", {}).items():
                        self.versions[agent_name] = {}
                        for version_str, version_data in versions_data.items():
                            version = AgentVersion(
                                agent_name=agent_name,
                                version=version_str,
                                version_type=VersionType(version_data["version_type"]),
                                code=version_data["code"],
                                description=version_data["description"],
                                changelog=version_data.get("changelog", []),
                                dependencies=version_data.get("dependencies", {}),
                                created_at=datetime.fromisoformat(version_data.get("created_at", datetime.now().isoformat())),
                                created_by=version_data.get("created_by"),
                                is_active=version_data.get("is_active", False),
                                metadata=version_data.get("metadata", {})
                            )
                            self.versions[agent_name][version_str] = version
                    
                    self.active_versions = data.get("active_versions", {})
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Versionen: {e}")
    
    def _save_data(self):
        """Speichert Daten in Storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "versions": {
                    agent_name: {
                        version_str: {
                            "version": version.version,
                            "version_type": version.version_type.value,
                            "code": version.code,
                            "description": version.description,
                            "changelog": version.changelog,
                            "dependencies": version.dependencies,
                            "created_at": version.created_at.isoformat(),
                            "created_by": version.created_by,
                            "is_active": version.is_active,
                            "metadata": version.metadata
                        }
                        for version_str, version in versions.items()
                    }
                    for agent_name, versions in self.versions.items()
                },
                "active_versions": self.active_versions
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Versionen: {e}")
    
    def _parse_version(self, version_str: str) -> tuple:
        """Parst Semantic Version (major.minor.patch)"""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(\w+))?$', version_str)
        if not match:
            raise ValueError(f"Ungültige Version: {version_str}")
        return tuple(map(int, match.groups()[:3]))
    
    def _increment_version(self, current_version: str, version_type: VersionType) -> str:
        """Erhöht Version"""
        major, minor, patch = self._parse_version(current_version)
        
        if version_type == VersionType.MAJOR:
            return f"{major + 1}.0.0"
        elif version_type == VersionType.MINOR:
            return f"{major}.{minor + 1}.0"
        else:  # PATCH
            return f"{major}.{minor}.{patch + 1}"
    
    def create_version(
        self,
        agent_name: str,
        code: str,
        description: str,
        version_type: VersionType = VersionType.PATCH,
        changelog: List[str] = None,
        dependencies: Dict[str, str] = None,
        created_by: Optional[str] = None
    ) -> AgentVersion:
        """
        Erstellt neue Version
        
        Args:
            agent_name: Agent Name
            code: Agent Code
            description: Beschreibung
            version_type: Version Type
            changelog: Changelog
            dependencies: Dependencies
            created_by: Ersteller
        
        Returns:
            AgentVersion
        """
        if agent_name not in self.versions:
            self.versions[agent_name] = {}
        
        # Bestimme nächste Version
        existing_versions = list(self.versions[agent_name].keys())
        if existing_versions:
            latest_version = max(existing_versions, key=lambda v: self._parse_version(v))
            new_version = self._increment_version(latest_version, version_type)
        else:
            new_version = "1.0.0"
        
        version = AgentVersion(
            agent_name=agent_name,
            version=new_version,
            version_type=version_type,
            code=code,
            description=description,
            changelog=changelog or [],
            dependencies=dependencies or {},
            created_by=created_by
        )
        
        self.versions[agent_name][new_version] = version
        self._save_data()
        
        logger.info(f"Version {new_version} für Agent {agent_name} erstellt")
        return version
    
    def activate_version(self, agent_name: str, version: str) -> bool:
        """
        Aktiviert Version
        
        Args:
            agent_name: Agent Name
            version: Version
        
        Returns:
            True wenn erfolgreich
        """
        if agent_name not in self.versions or version not in self.versions[agent_name]:
            return False
        
        # Deaktiviere alle anderen Versionen
        for v in self.versions[agent_name].values():
            v.is_active = (v.version == version)
        
        self.active_versions[agent_name] = version
        self._save_data()
        
        logger.info(f"Version {version} für Agent {agent_name} aktiviert")
        return True
    
    def rollback(self, agent_name: str, target_version: Optional[str] = None) -> bool:
        """
        Rollback zu älterer Version
        
        Args:
            agent_name: Agent Name
            target_version: Ziel-Version (optional, nutzt vorherige wenn None)
        
        Returns:
            True wenn erfolgreich
        """
        if agent_name not in self.versions:
            return False
        
        versions = sorted(
            self.versions[agent_name].keys(),
            key=lambda v: self._parse_version(v),
            reverse=True
        )
        
        if not versions:
            return False
        
        if target_version:
            if target_version not in versions:
                return False
            rollback_version = target_version
        else:
            # Rollback zu vorheriger Version
            current = self.active_versions.get(agent_name)
            if current and current in versions:
                current_idx = versions.index(current)
                if current_idx < len(versions) - 1:
                    rollback_version = versions[current_idx + 1]
                else:
                    return False  # Bereits älteste Version
            else:
                rollback_version = versions[1] if len(versions) > 1 else versions[0]
        
        return self.activate_version(agent_name, rollback_version)
    
    def get_version_history(self, agent_name: str) -> List[AgentVersion]:
        """Holt Version History"""
        if agent_name not in self.versions:
            return []
        
        versions = list(self.versions[agent_name].values())
        return sorted(versions, key=lambda v: self._parse_version(v.version), reverse=True)
    
    def get_active_version(self, agent_name: str) -> Optional[AgentVersion]:
        """Holt aktive Version"""
        if agent_name not in self.active_versions:
            return None
        
        version_str = self.active_versions[agent_name]
        if agent_name in self.versions and version_str in self.versions[agent_name]:
            return self.versions[agent_name][version_str]
        return None
    
    def compare_versions(self, agent_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Vergleicht zwei Versionen"""
        if agent_name not in self.versions:
            return {"error": "Agent nicht gefunden"}
        
        if version1 not in self.versions[agent_name] or version2 not in self.versions[agent_name]:
            return {"error": "Version nicht gefunden"}
        
        v1 = self.versions[agent_name][version1]
        v2 = self.versions[agent_name][version2]
        
        v1_tuple = self._parse_version(version1)
        v2_tuple = self._parse_version(version2)
        
        return {
            "agent_name": agent_name,
            "version1": {
                "version": version1,
                "description": v1.description,
                "created_at": v1.created_at.isoformat(),
                "changelog": v1.changelog
            },
            "version2": {
                "version": version2,
                "description": v2.description,
                "created_at": v2.created_at.isoformat(),
                "changelog": v2.changelog
            },
            "newer": version1 if v1_tuple > v2_tuple else version2,
            "older": version2 if v1_tuple > v2_tuple else version1
        }


# Globale Version Manager-Instanz
_global_version_manager: Optional[AgentVersionManager] = None


def get_version_manager() -> AgentVersionManager:
    """Holt globale Version Manager-Instanz"""
    global _global_version_manager
    if _global_version_manager is None:
        _global_version_manager = AgentVersionManager()
    return _global_version_manager
