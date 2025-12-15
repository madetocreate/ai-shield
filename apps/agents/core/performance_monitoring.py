"""
Performance Monitoring & Optimization
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import time
import logging
import psutil
import asyncio

logger = logging.getLogger(__name__)

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    REQUEST_TIME = "request_time"
    DATABASE_QUERY = "database_query"
    LLM_CALL = "llm_call"

class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Bottleneck:
    id: str
    metric_type: MetricType
    severity: Severity
    description: str
    current_value: float
    threshold: float
    recommendation: str
    detected_at: datetime
    resolved: bool = False

@dataclass
class OptimizationRecommendation:
    id: str
    metric_type: MetricType
    title: str
    description: str
    impact: str
    estimated_improvement: str
    action: str
    created_at: datetime

class PerformanceMonitor:
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.bottlenecks: Dict[str, Bottleneck] = {}
        self.recommendations: List[OptimizationRecommendation] = []
        self.thresholds = {
            MetricType.CPU: 80.0,
            MetricType.MEMORY: 85.0,
            MetricType.DISK: 90.0,
            MetricType.REQUEST_TIME: 2.0,
            MetricType.DATABASE_QUERY: 1.0,
            MetricType.LLM_CALL: 5.0
        }
    
    def record_metric(self, metric_type: MetricType, value: float, unit: str = "", labels: Optional[Dict[str, str]] = None) -> PerformanceMetric:
        metric = PerformanceMetric(
            id=f"metric_{datetime.now().timestamp()}",
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self.metrics.append(metric)
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-10000:]
        self._check_bottleneck(metric)
        return metric
    
    def _check_bottleneck(self, metric: PerformanceMetric):
        threshold = self.thresholds.get(metric.metric_type)
        if not threshold or metric.value <= threshold:
            return
        severity = Severity.WARNING
        if metric.value > threshold * 1.5:
            severity = Severity.ERROR
        if metric.value > threshold * 2.0:
            severity = Severity.CRITICAL
        recommendation = f"{metric.metric_type.value} exceeds threshold. Consider optimization."
        bottleneck = Bottleneck(
            id=f"{metric.metric_type.value}_{metric.labels.get('agent', 'system')}",
            metric_type=metric.metric_type,
            severity=severity,
            description=f"{metric.metric_type.value} exceeds threshold: {metric.value:.2f} > {threshold:.2f}",
            current_value=metric.value,
            threshold=threshold,
            recommendation=recommendation,
            detected_at=datetime.now()
        )
        self.bottlenecks[bottleneck.id] = bottleneck
    
    async def collect_system_metrics(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric(MetricType.CPU, cpu_percent, unit="%", labels={"type": "system"})
            memory = psutil.virtual_memory()
            self.record_metric(MetricType.MEMORY, memory.percent, unit="%", labels={"type": "system"})
            disk = psutil.disk_usage('/')
            self.record_metric(MetricType.DISK, disk.percent, unit="%", labels={"type": "system"})
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von System-Metriken: {e}")
    
    def get_metrics(self, metric_type: Optional[MetricType] = None, limit: int = 1000) -> List[PerformanceMetric]:
        metrics = self.metrics.copy()
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        metrics.sort(key=lambda x: x.timestamp, reverse=True)
        return metrics[:limit]
    
    def get_bottlenecks(self, severity: Optional[Severity] = None, resolved: Optional[bool] = None) -> List[Bottleneck]:
        bottlenecks = list(self.bottlenecks.values())
        if severity:
            bottlenecks = [b for b in bottlenecks if b.severity == severity]
        if resolved is not None:
            bottlenecks = [b for b in bottlenecks if b.resolved == resolved]
        bottlenecks.sort(key=lambda x: x.detected_at, reverse=True)
        return bottlenecks
    
    def resolve_bottleneck(self, bottleneck_id: str):
        if bottleneck_id in self.bottlenecks:
            self.bottlenecks[bottleneck_id].resolved = True
    
    def generate_recommendations(self) -> List[OptimizationRecommendation]:
        recommendations = []
        recent_metrics = self.get_metrics(limit=1000)
        cpu_metrics = [m for m in recent_metrics if m.metric_type == MetricType.CPU]
        if cpu_metrics:
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 70:
                recommendations.append(OptimizationRecommendation(
                    id=f"rec_{datetime.now().timestamp()}_1",
                    metric_type=MetricType.CPU,
                    title="High CPU Usage",
                    description=f"Average CPU usage is {avg_cpu:.1f}%",
                    impact="high",
                    estimated_improvement="20-30%",
                    action="Consider horizontal scaling or code optimization",
                    created_at=datetime.now()
                ))
        self.recommendations.extend(recommendations)
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        recent_metrics = self.get_metrics(limit=1000)
        stats = {}
        for metric_type in MetricType:
            type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
            if type_metrics:
                values = [m.value for m in type_metrics]
                stats[metric_type.value] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
        return stats

_global_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor
