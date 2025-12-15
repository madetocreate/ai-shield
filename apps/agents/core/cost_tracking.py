"""
Cost Tracking & Billing - Cost Tracking, Billing API, Cost Alerts

Features:
- Cost Tracking pro Account/Agent
- Billing Integration
- Cost Alerts
- Usage Reports
- Cost Optimization Recommendations
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import logging

logger = logging.getLogger(__name__)


class CostType(str, Enum):
    """Cost Type"""
    LLM_API = "llm_api"  # LLM API Calls
    STORAGE = "storage"  # Storage Costs
    COMPUTE = "compute"  # Compute Costs
    NETWORK = "network"  # Network Costs
    INTEGRATION = "integration"  # External Integration Costs


@dataclass
class CostEntry:
    """Cost Entry"""
    account_id: str
    agent_name: Optional[str] = None
    cost_type: CostType = CostType.LLM_API
    amount: float = 0.0  # In USD
    quantity: float = 0.0  # Anzahl (z.B. API Calls)
    unit_price: float = 0.0  # Preis pro Einheit
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostAlert:
    """Cost Alert"""
    account_id: str
    threshold: float
    current_cost: float
    period: str  # daily, weekly, monthly
    alert_level: str = "warning"  # warning, critical
    timestamp: datetime = field(default_factory=datetime.now)


class CostTracker:
    """
    Cost Tracker
    
    Trackt Kosten pro Account/Agent.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialisiert Cost Tracker
        
        Args:
            storage_path: Pfad für Storage
        """
        self.storage_path = storage_path or os.getenv(
            "COST_STORAGE_PATH",
            "data/costs.json"
        )
        self.cost_entries: List[CostEntry] = []
        self.cost_alerts: List[CostAlert] = []
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}  # account_id -> {period -> threshold}
        self._load_data()
    
    def _load_data(self):
        """Lädt Daten aus Storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.cost_entries = [
                        CostEntry(
                            account_id=e["account_id"],
                            agent_name=e.get("agent_name"),
                            cost_type=CostType(e.get("cost_type", "llm_api")),
                            amount=e["amount"],
                            quantity=e.get("quantity", 0.0),
                            unit_price=e.get("unit_price", 0.0),
                            timestamp=datetime.fromisoformat(e.get("timestamp", datetime.now().isoformat())),
                            metadata=e.get("metadata", {})
                        )
                        for e in data.get("cost_entries", [])
                    ]
                    
                    self.alert_thresholds = data.get("alert_thresholds", {})
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Kosten: {e}")
    
    def _save_data(self):
        """Speichert Daten in Storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "cost_entries": [
                    {
                        "account_id": e.account_id,
                        "agent_name": e.agent_name,
                        "cost_type": e.cost_type.value,
                        "amount": e.amount,
                        "quantity": e.quantity,
                        "unit_price": e.unit_price,
                        "timestamp": e.timestamp.isoformat(),
                        "metadata": e.metadata
                    }
                    for e in self.cost_entries
                ],
                "alert_thresholds": self.alert_thresholds
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Kosten: {e}")
    
    def track_cost(
        self,
        account_id: str,
        cost_type: CostType,
        amount: float,
        quantity: float = 1.0,
        unit_price: Optional[float] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Trackt Kosten
        
        Args:
            account_id: Account ID
            cost_type: Cost Type
            amount: Betrag in USD
            quantity: Anzahl
            unit_price: Preis pro Einheit
            agent_name: Agent Name (optional)
            metadata: Zusätzliche Metadaten
        """
        entry = CostEntry(
            account_id=account_id,
            agent_name=agent_name,
            cost_type=cost_type,
            amount=amount,
            quantity=quantity,
            unit_price=unit_price or (amount / quantity if quantity > 0 else 0.0),
            metadata=metadata or {}
        )
        
        self.cost_entries.append(entry)
        
        # Prüfe Alerts
        self._check_alerts(account_id)
        
        # Speichere (alle 100 Einträge)
        if len(self.cost_entries) % 100 == 0:
            self._save_data()
    
    def _check_alerts(self, account_id: str):
        """Prüft Cost Alerts"""
        if account_id not in self.alert_thresholds:
            return
        
        thresholds = self.alert_thresholds[account_id]
        
        for period, threshold in thresholds.items():
            current_cost = self.get_total_cost(account_id, period=period)
            
            if current_cost >= threshold:
                alert_level = "critical" if current_cost >= threshold * 1.5 else "warning"
                
                alert = CostAlert(
                    account_id=account_id,
                    threshold=threshold,
                    current_cost=current_cost,
                    period=period,
                    alert_level=alert_level
                )
                
                self.cost_alerts.append(alert)
                logger.warning(f"Cost Alert: {account_id} hat {current_cost:.2f} USD erreicht (Threshold: {threshold:.2f})")
    
    def get_total_cost(
        self,
        account_id: str,
        period: str = "monthly",
        agent_name: Optional[str] = None,
        cost_type: Optional[CostType] = None
    ) -> float:
        """
        Berechnet Gesamtkosten
        
        Args:
            account_id: Account ID
            period: daily, weekly, monthly
            agent_name: Agent Name (optional)
            cost_type: Cost Type (optional)
        
        Returns:
            Gesamtkosten in USD
        """
        now = datetime.now()
        
        if period == "daily":
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(weeks=1)
        else:  # monthly
            start_date = now - timedelta(days=30)
        
        filtered = [
            e for e in self.cost_entries
            if e.account_id == account_id
            and e.timestamp >= start_date
            and (agent_name is None or e.agent_name == agent_name)
            and (cost_type is None or e.cost_type == cost_type)
        ]
        
        return sum(e.amount for e in filtered)
    
    def get_cost_breakdown(
        self,
        account_id: str,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """Holt Cost Breakdown"""
        total = self.get_total_cost(account_id, period=period)
        
        breakdown = {}
        for cost_type in CostType:
            cost = self.get_total_cost(account_id, period=period, cost_type=cost_type)
            if cost > 0:
                breakdown[cost_type.value] = {
                    "amount": cost,
                    "percentage": (cost / total * 100) if total > 0 else 0.0
                }
        
        return {
            "account_id": account_id,
            "period": period,
            "total": total,
            "breakdown": breakdown
        }
    
    def set_alert_threshold(self, account_id: str, period: str, threshold: float):
        """Setzt Alert Threshold"""
        if account_id not in self.alert_thresholds:
            self.alert_thresholds[account_id] = {}
        self.alert_thresholds[account_id][period] = threshold
        self._save_data()
    
    def get_active_alerts(self, account_id: Optional[str] = None) -> List[CostAlert]:
        """Holt aktive Alerts"""
        alerts = self.cost_alerts
        if account_id:
            alerts = [a for a in alerts if a.account_id == account_id]
        return alerts


# Globale Cost Tracker-Instanz
_global_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Holt globale Cost Tracker-Instanz"""
    global _global_cost_tracker
    if _global_cost_tracker is None:
        _global_cost_tracker = CostTracker()
    return _global_cost_tracker
