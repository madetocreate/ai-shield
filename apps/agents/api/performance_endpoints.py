"""
Performance Monitoring API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from apps.agents.core.performance_monitoring import get_performance_monitor, MetricType, Severity

router = APIRouter(prefix="/api/v1/performance", tags=["performance"])

class PerformanceMetricResponse(BaseModel):
    id: str
    metric_type: str
    value: float
    unit: str
    timestamp: str
    labels: Dict[str, str]

class BottleneckResponse(BaseModel):
    id: str
    metric_type: str
    severity: str
    description: str
    current_value: float
    threshold: float
    recommendation: str
    detected_at: str
    resolved: bool

@router.get("/metrics", response_model=List[PerformanceMetricResponse])
async def get_metrics(metric_type: Optional[str] = Query(None), limit: int = Query(1000, le=10000)):
    monitor = get_performance_monitor()
    metric_type_enum = None
    if metric_type:
        try:
            metric_type_enum = MetricType(metric_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Metric Type: {metric_type}")
    metrics = monitor.get_metrics(metric_type=metric_type_enum, limit=limit)
    return [PerformanceMetricResponse(id=m.id, metric_type=m.metric_type.value, value=m.value, unit=m.unit, timestamp=m.timestamp.isoformat(), labels=m.labels) for m in metrics]

@router.get("/bottlenecks", response_model=List[BottleneckResponse])
async def get_bottlenecks(severity: Optional[str] = Query(None), resolved: Optional[bool] = Query(None)):
    monitor = get_performance_monitor()
    severity_enum = None
    if severity:
        try:
            severity_enum = Severity(severity)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültige Severity: {severity}")
    bottlenecks = monitor.get_bottlenecks(severity=severity_enum, resolved=resolved)
    return [BottleneckResponse(id=b.id, metric_type=b.metric_type.value, severity=b.severity.value, description=b.description, current_value=b.current_value, threshold=b.threshold, recommendation=b.recommendation, detected_at=b.detected_at.isoformat(), resolved=b.resolved) for b in bottlenecks]

@router.post("/bottlenecks/{bottleneck_id}/resolve")
async def resolve_bottleneck(bottleneck_id: str):
    monitor = get_performance_monitor()
    monitor.resolve_bottleneck(bottleneck_id)
    return {"success": True}

@router.get("/statistics")
async def get_statistics():
    monitor = get_performance_monitor()
    return {"statistics": monitor.get_statistics()}

@router.post("/collect-system-metrics")
async def collect_system_metrics():
    monitor = get_performance_monitor()
    await monitor.collect_system_metrics()
    return {"success": True}
