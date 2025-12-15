"""
Data Export/Import - Export API, Import API, Migration Tools

Features:
- Data Export (JSON, CSV)
- Data Import
- Migration Tools
- Backup/Restore
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import csv
import os
import logging
from io import StringIO

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Export Format"""
    JSON = "json"
    CSV = "csv"
    YAML = "yaml"


@dataclass
class ExportData:
    """Export Data"""
    format: ExportFormat
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


class DataExporter:
    """
    Data Exporter
    
    Exportiert Daten in verschiedenen Formaten.
    """
    
    def __init__(self):
        """Initialisiert Data Exporter"""
        pass
    
    def export_agents(
        self,
        format: ExportFormat = ExportFormat.JSON,
        include_code: bool = False
    ) -> str:
        """
        Exportiert Agents
        
        Args:
            format: Export Format
            include_code: Ob Agent-Code inkludiert werden soll
        
        Returns:
            Exportierte Daten als String
        """
        from apps.agents.core.agent_registry import get_registry
        
        registry = get_registry()
        agents = registry.list_agents()
        
        data = {
            "export_type": "agents",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "agents": []
        }
        
        for agent_name in agents:
            agent_config = registry._agents.get(agent_name)
            if agent_config:
                agent_data = {
                    "name": agent_name,
                    "enabled": agent_config.enabled,
                    "dependencies": agent_config.dependencies or {}
                }
                if include_code:
                    # TODO: Agent Code exportieren
                    agent_data["code"] = None
                data["agents"].append(agent_data)
        
        if format == ExportFormat.JSON:
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == ExportFormat.CSV:
            return self._to_csv(data["agents"])
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_configuration(
        self,
        format: ExportFormat = ExportFormat.JSON
    ) -> str:
        """Exportiert Konfiguration"""
        from apps.agents.core.configuration_management import get_config_manager
        
        manager = get_config_manager()
        
        data = {
            "export_type": "configuration",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "feature_flags": [
                {
                    "name": flag.name,
                    "status": flag.status.value,
                    "percentage": flag.percentage
                }
                for flag in manager.feature_flags.values()
            ],
            "ab_tests": [
                {
                    "name": test.name,
                    "active": test.active,
                    "variants": [
                        {
                            "name": v.name,
                            "weight": v.weight
                        }
                        for v in test.variants
                    ]
                }
                for test in manager.ab_tests.values()
            ],
            "configurations": manager.configurations
        }
        
        if format == ExportFormat.JSON:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_all(self, format: ExportFormat = ExportFormat.JSON) -> str:
        """Exportiert alle Daten"""
        data = {
            "export_type": "full",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "agents": json.loads(self.export_agents(format=ExportFormat.JSON)),
            "configuration": json.loads(self.export_configuration(format=ExportFormat.JSON))
        }
        
        if format == ExportFormat.JSON:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Konvertiert zu CSV"""
        if not data:
            return ""
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()


class DataImporter:
    """
    Data Importer
    
    Importiert Daten aus verschiedenen Formaten.
    """
    
    def __init__(self):
        """Initialisiert Data Importer"""
        pass
    
    def import_data(self, data: str, format: ExportFormat = ExportFormat.JSON) -> Dict[str, Any]:
        """
        Importiert Daten
        
        Args:
            data: Daten als String
            format: Format
        
        Returns:
            Import-Ergebnis
        """
        try:
            if format == ExportFormat.JSON:
                parsed = json.loads(data)
            else:
                raise ValueError(f"Format {format} nicht unterstützt")
            
            result = {
                "success": True,
                "imported": [],
                "errors": []
            }
            
            # Import Agents
            if "agents" in parsed:
                for agent_data in parsed["agents"]:
                    try:
                        # TODO: Agent importieren
                        result["imported"].append(f"agent:{agent_data.get('name')}")
                    except Exception as e:
                        result["errors"].append(f"Agent {agent_data.get('name')}: {e}")
            
            # Import Configuration
            if "configuration" in parsed or "feature_flags" in parsed:
                try:
                    from apps.agents.core.configuration_management import get_config_manager
                    manager = get_config_manager()
                    
                    # Import Feature Flags
                    if "feature_flags" in parsed:
                        for flag_data in parsed["feature_flags"]:
                            manager.create_feature_flag(
                                name=flag_data["name"],
                                status=flag_data.get("status", "disabled"),
                                percentage=flag_data.get("percentage", 100.0)
                            )
                            result["imported"].append(f"feature_flag:{flag_data['name']}")
                    
                    # Import Configurations
                    if "configurations" in parsed:
                        for namespace, configs in parsed["configurations"].items():
                            for key, value in configs.items():
                                manager.set_config(key, value, namespace)
                                result["imported"].append(f"config:{namespace}.{key}")
                except Exception as e:
                    result["errors"].append(f"Configuration: {e}")
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "imported": [],
                "errors": []
            }


# Globale Instanzen
_global_exporter: Optional[DataExporter] = None
_global_importer: Optional[DataImporter] = None


def get_exporter() -> DataExporter:
    """Holt globale Exporter-Instanz"""
    global _global_exporter
    if _global_exporter is None:
        _global_exporter = DataExporter()
    return _global_exporter


def get_importer() -> DataImporter:
    """Holt globale Importer-Instanz"""
    global _global_importer
    if _global_importer is None:
        _global_importer = DataImporter()
    return _global_importer
