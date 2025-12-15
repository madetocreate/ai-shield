"""
Real-time API Endpoints - WebSocket für Live Monitoring

Endpoints:
- WS /api/v1/realtime/ws - WebSocket für Live Updates
- GET /api/v1/realtime/metrics - Aktuelle Metrics
- GET /api/v1/realtime/alerts - Aktive Alerts
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
from apps.agents.core.real_time_monitoring import get_real_time_monitor, RealTimeMetric, AlertLevel
from apps.agents.core.monitoring import get_monitor
import json

router = APIRouter(prefix="/api/v1/realtime", tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket Endpoint für Live Updates
    
    Sendet:
    - Metrics (real-time)
    - Alerts
    - Agent Status Updates
    """
    await websocket.accept()
    monitor = get_real_time_monitor()
    monitor.register_connection(websocket)
    
    try:
        # Sende initiale Daten
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket verbunden"
        })
        
        # Halte Verbindung offen
        while True:
            # Empfange Nachrichten (optional)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle Client Messages (z.B. Subscribe/Unsubscribe)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        monitor.unregister_connection(websocket)
    except Exception as e:
        logger.error(f"WebSocket Fehler: {e}")
        monitor.unregister_connection(websocket)


@router.get("/metrics")
async def get_current_metrics() -> Dict[str, Any]:
    """Holt aktuelle Metrics"""
    monitor = get_real_time_monitor()
    
    # Konvertiere Metrics History zu Dict
    metrics = {}
    for name, history in monitor.metrics_history.items():
        if history:
            latest = history[-1]
            metrics[name] = {
                "value": latest.value,
                "labels": latest.labels,
                "timestamp": latest.timestamp.isoformat()
            }
    
    return {"metrics": metrics}


@router.get("/alerts")
async def get_active_alerts() -> Dict[str, Any]:
    """Holt aktive Alerts"""
    monitor = get_real_time_monitor()
    alerts = monitor.get_active_alerts()
    
    return {
        "alerts": [
            {
                "id": a.id,
                "level": a.level.value,
                "title": a.title,
                "message": a.message,
                "agent_name": a.agent_name,
                "account_id": a.account_id,
                "timestamp": a.timestamp.isoformat()
            }
            for a in alerts
        ],
        "count": len(alerts)
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Löst Alert auf"""
    monitor = get_real_time_monitor()
    monitor.resolve_alert(alert_id)
    return {"success": True, "message": f"Alert {alert_id} aufgelöst"}


import logging
logger = logging.getLogger(__name__)
