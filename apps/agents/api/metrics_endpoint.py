"""
Prometheus Metrics Endpoint

Stellt Metrics im Prometheus-Format bereit.
Kann von Prometheus gescraped werden.
"""

from fastapi import APIRouter
from apps.agents.core.monitoring import get_monitor

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/")
def get_metrics():
    """
    Prometheus Metrics Endpoint
    
    Returns:
        Metrics im Prometheus-Format
    """
    monitor = get_monitor()
    metrics = monitor.export_prometheus_metrics()
    return metrics


@router.get("/health")
def health():
    """Health Check"""
    return {"status": "ok"}
