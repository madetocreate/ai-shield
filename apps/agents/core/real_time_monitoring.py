"""
Real-time Monitoring - WebSocket-basiertes Live Monitoring

Features:
- WebSocket-basierte Live Updates
- Real-time Metrics
- Live Agent Status
- Performance Tracking
- Alert System
"""

from typing import Dict, Optional, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert Level"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert"""
    id: str
    level: AlertLevel
    title: str
    message: str
    agent_name: Optional[str] = None
    account_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RealTimeMetric:
    """Real-time Metric"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class RealTimeMonitor:
    """
    Real-time Monitor
    
    Verwaltet WebSocket-Verbindungen und sendet Live-Updates.
    """
    
    def __init__(self):
        """Initialisiert Real-time Monitor"""
        self.connections: List[Any] = []  # WebSocket Connections
        self.metrics_buffer: List[RealTimeMetric] = []
        self.alerts: Dict[str, Alert] = {}
        self.alert_callbacks: List[Callable] = []
        self.metrics_history: Dict[str, List[RealTimeMetric]] = {}
    
    def register_connection(self, websocket: Any):
        """Registriert WebSocket-Verbindung"""
        self.connections.append(websocket)
        logger.info(f"WebSocket-Verbindung registriert (Total: {len(self.connections)})")
    
    def unregister_connection(self, websocket: Any):
        """Entfernt WebSocket-Verbindung"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            logger.info(f"WebSocket-Verbindung entfernt (Total: {len(self.connections)})")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Sendet Nachricht an alle verbundenen Clients
        
        Args:
            message: Nachricht als Dict
        """
        if not self.connections:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = []
        
        for connection in self.connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.warning(f"Fehler beim Senden: {e}")
                disconnected.append(connection)
        
        # Entferne getrennte Verbindungen
        for conn in disconnected:
            self.unregister_connection(conn)
    
    async def send_metric(self, metric: RealTimeMetric):
        """Sendet Metric an alle Clients"""
        self.metrics_buffer.append(metric)
        
        # Speichere in History
        if metric.name not in self.metrics_history:
            self.metrics_history[metric.name] = []
        self.metrics_history[metric.name].append(metric)
        
        # Behalte nur letzte 1000
        if len(self.metrics_history[metric.name]) > 1000:
            self.metrics_history[metric.name] = self.metrics_history[metric.name][-1000:]
        
        await self.broadcast({
            "type": "metric",
            "data": {
                "name": metric.name,
                "value": metric.value,
                "labels": metric.labels,
                "timestamp": metric.timestamp.isoformat()
            }
        })
    
    async def send_alert(self, alert: Alert):
        """Sendet Alert an alle Clients"""
        self.alerts[alert.id] = alert
        
        await self.broadcast({
            "type": "alert",
            "data": {
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "agent_name": alert.agent_name,
                "account_id": alert.account_id,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            }
        })
        
        # Rufe Alert-Callbacks auf
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert-Callback Fehler: {e}")
    
    def create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        agent_name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> Alert:
        """Erstellt Alert"""
        alert_id = f"{agent_name or 'system'}_{datetime.now().timestamp()}"
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            agent_name=agent_name,
            account_id=account_id
        )
        
        # Sende asynchron
        asyncio.create_task(self.send_alert(alert))
        
        return alert
    
    def register_alert_callback(self, callback: Callable):
        """Registriert Alert-Callback"""
        self.alert_callbacks.append(callback)
    
    def get_active_alerts(self) -> List[Alert]:
        """Holt aktive Alerts"""
        return [a for a in self.alerts.values() if not a.resolved]
    
    def resolve_alert(self, alert_id: str):
        """Löst Alert auf"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            asyncio.create_task(self.broadcast({
                "type": "alert_resolved",
                "data": {"id": alert_id}
            }))


# Globale Real-time Monitor-Instanz
_global_real_time_monitor: Optional[RealTimeMonitor] = None


def get_real_time_monitor() -> RealTimeMonitor:
    """Holt globale Real-time Monitor-Instanz"""
    global _global_real_time_monitor
    if _global_real_time_monitor is None:
        _global_real_time_monitor = RealTimeMonitor()
    return _global_real_time_monitor
