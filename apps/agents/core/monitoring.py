"""
Monitoring & Observability für Agents

Trackt:
- Request-Rate pro Agent
- Routing-Entscheidungen
- Handoff-Rate
- Consent-Checks
- Error-Rate
- Performance-Metrics
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
from collections import defaultdict


class MetricType(str, Enum):
    """Metric-Typen"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class AgentMetric:
    """Agent-Metric"""
    agent_name: str
    metric_type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AgentMonitor:
    """
    Monitor für Agent-Performance und Observability
    
    Trackt Metrics, Errors, Performance
    """
    
    def __init__(self):
        self.metrics: Dict[str, list] = defaultdict(list)
        self.errors: list = []
        self.request_times: Dict[str, list] = defaultdict(list)
        self.routing_decisions: list = []
        self.handoffs: list = []
        self.consent_checks: list = []
    
    def track_request(
        self,
        agent_name: str,
        account_id: str,
        duration: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Trackt Request"""
        metric = AgentMetric(
            agent_name=agent_name,
            metric_type=MetricType.HISTOGRAM,
            value=duration,
            labels={
                "account_id": account_id,
                "success": str(success)
            }
        )
        self.metrics[f"{agent_name}_requests"].append(metric)
        self.request_times[agent_name].append(duration)
        
        if not success and error:
            self.errors.append({
                "agent": agent_name,
                "account_id": account_id,
                "error": error,
                "timestamp": datetime.now()
            })
    
    def track_routing_decision(
        self,
        account_id: str,
        source_agent: str,
        target_agent: str,
        intent: str,
        confidence: float
    ):
        """Trackt Routing-Entscheidung"""
        self.routing_decisions.append({
            "account_id": account_id,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now()
        })
    
    def track_handoff(
        self,
        account_id: str,
        reason: str,
        priority: str,
        method: str
    ):
        """Trackt Handoff"""
        self.handoffs.append({
            "account_id": account_id,
            "reason": reason,
            "priority": priority,
            "method": method,
            "timestamp": datetime.now()
        })
    
    def track_consent_check(
        self,
        account_id: str,
        category: str,
        granted: bool
    ):
        """Trackt Consent-Check"""
        self.consent_checks.append({
            "account_id": account_id,
            "category": category,
            "granted": granted,
            "timestamp": datetime.now()
        })
    
    def get_agent_stats(
        self,
        agent_name: str,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Holt Agent-Statistiken"""
        cutoff = datetime.now().timestamp() - (time_window_minutes * 60)
        
        recent_requests = [
            r for r in self.request_times.get(agent_name, [])
            if r > cutoff
        ]
        
        recent_errors = [
            e for e in self.errors
            if e["agent"] == agent_name and e["timestamp"].timestamp() > cutoff
        ]
        
        if not recent_requests:
            return {
                "agent": agent_name,
                "requests": 0,
                "errors": 0,
                "avg_duration": 0.0,
                "error_rate": 0.0
            }
        
        return {
            "agent": agent_name,
            "requests": len(recent_requests),
            "errors": len(recent_errors),
            "avg_duration": sum(recent_requests) / len(recent_requests),
            "error_rate": len(recent_errors) / len(recent_requests) if recent_requests else 0.0
        }
    
    def get_routing_stats(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Holt Routing-Statistiken"""
        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        
        recent = [r for r in self.routing_decisions if r["timestamp"] > cutoff]
        
        if not recent:
            return {
                "total": 0,
                "by_target_agent": {},
                "by_intent": {}
            }
        
        by_target = defaultdict(int)
        by_intent = defaultdict(int)
        
        for r in recent:
            by_target[r["target_agent"]] += 1
            by_intent[r["intent"]] += 1
        
        return {
            "total": len(recent),
            "by_target_agent": dict(by_target),
            "by_intent": dict(by_intent)
        }
    
    def get_handoff_stats(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Holt Handoff-Statistiken"""
        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        
        recent = [h for h in self.handoffs if h["timestamp"] > cutoff]
        
        if not recent:
            return {
                "total": 0,
                "by_reason": {},
                "by_priority": {}
            }
        
        by_reason = defaultdict(int)
        by_priority = defaultdict(int)
        
        for h in recent:
            by_reason[h["reason"]] += 1
            by_priority[h["priority"]] += 1
        
        return {
            "total": len(recent),
            "by_reason": dict(by_reason),
            "by_priority": dict(by_priority)
        }
    
    def export_prometheus_metrics(self) -> str:
        """Exportiert Metrics im Prometheus-Format"""
        lines = []
        
        # Request Metrics
        for agent_name, times in self.request_times.items():
            if times:
                lines.append(f"# TYPE agent_requests_total counter")
                lines.append(f'agent_requests_total{{agent="{agent_name}"}} {len(times)}')
                lines.append(f"# TYPE agent_request_duration_seconds histogram")
                lines.append(f'agent_request_duration_seconds{{agent="{agent_name}"}} {sum(times) / len(times)}')
        
        # Error Metrics
        error_counts = defaultdict(int)
        for error in self.errors:
            error_counts[error["agent"]] += 1
        
        for agent, count in error_counts.items():
            lines.append(f'agent_errors_total{{agent="{agent}"}} {count}')
        
        # Handoff Metrics
        lines.append(f"agent_handoffs_total {len(self.handoffs)}")
        
        # Consent Check Metrics
        consent_granted = sum(1 for c in self.consent_checks if c["granted"])
        lines.append(f"agent_consent_checks_total {len(self.consent_checks)}")
        lines.append(f"agent_consent_granted_total {consent_granted}")
        
        return "\n".join(lines)


# Globale Monitor-Instanz
_global_monitor: Optional[AgentMonitor] = None


def get_monitor() -> AgentMonitor:
    """Holt globale Monitor-Instanz"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AgentMonitor()
    return _global_monitor


# Context Manager für Request-Tracking
class RequestTracker:
    """Context Manager für Request-Tracking"""
    
    def __init__(self, agent_name: str, account_id: str):
        self.agent_name = agent_name
        self.account_id = account_id
        self.start_time = None
        self.monitor = get_monitor()
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        
        self.monitor.track_request(
            agent_name=self.agent_name,
            account_id=self.account_id,
            duration=duration,
            success=success,
            error=error
        )
        
        return False  # Don't suppress exceptions
