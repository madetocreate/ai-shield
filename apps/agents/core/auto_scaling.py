"""
Auto-Scaling - Automatische Skalierung, Resource Management, Cost Optimization

Features:
- Automatic Scaling basierend auf Load
- Resource Management
- Cost Optimization
- Performance Monitoring
- Scaling Policies
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class ScalingAction(str, Enum):
    """Scaling Actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"


@dataclass
class ResourceMetrics:
    """Resource Metrics"""
    cpu_usage: float  # 0.0 - 1.0
    memory_usage: float  # 0.0 - 1.0
    request_rate: float  # Requests pro Sekunde
    error_rate: float  # 0.0 - 1.0
    response_time_ms: float  # Millisekunden
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingPolicy:
    """Scaling Policy"""
    name: str
    min_instances: int = 1
    max_instances: int = 10
    target_cpu: float = 0.7  # Target CPU Usage
    target_memory: float = 0.7  # Target Memory Usage
    scale_up_threshold: float = 0.8  # Scale up wenn über diesem Wert
    scale_down_threshold: float = 0.3  # Scale down wenn unter diesem Wert
    cooldown_seconds: int = 300  # 5 Minuten Cooldown
    enabled: bool = True


@dataclass
class ScalingDecision:
    """Scaling Decision"""
    action: ScalingAction
    current_instances: int
    target_instances: int
    reason: str
    metrics: ResourceMetrics
    timestamp: datetime = field(default_factory=datetime.now)


class AutoScaler:
    """
    Auto-Scaler
    
    Skaliert automatisch basierend auf Metriken.
    """
    
    def __init__(self, policy: Optional[ScalingPolicy] = None):
        """
        Initialisiert Auto-Scaler
        
        Args:
            policy: Scaling Policy
        """
        self.policy = policy or ScalingPolicy(name="default")
        self.current_instances: Dict[str, int] = {}  # service_name -> instances
        self.last_scaling_action: Dict[str, datetime] = {}  # service_name -> last_action
        self.metrics_history: Dict[str, List[ResourceMetrics]] = {}  # service_name -> metrics
        self.monitoring_enabled = True
    
    def update_metrics(self, service_name: str, metrics: ResourceMetrics):
        """
        Aktualisiert Metriken für Service
        
        Args:
            service_name: Service Name
            metrics: Resource Metrics
        """
        if service_name not in self.metrics_history:
            self.metrics_history[service_name] = []
        
        self.metrics_history[service_name].append(metrics)
        
        # Behalte nur letzte 100 Metriken
        if len(self.metrics_history[service_name]) > 100:
            self.metrics_history[service_name] = self.metrics_history[service_name][-100:]
    
    def should_scale(self, service_name: str) -> ScalingDecision:
        """
        Prüft ob Skalierung nötig ist
        
        Args:
            service_name: Service Name
        
        Returns:
            ScalingDecision
        """
        if not self.policy.enabled:
            return ScalingDecision(
                action=ScalingAction.NO_ACTION,
                current_instances=self.current_instances.get(service_name, 1),
                target_instances=self.current_instances.get(service_name, 1),
                reason="Scaling disabled",
                metrics=ResourceMetrics(0, 0, 0, 0, 0)
            )
        
        # Prüfe Cooldown
        if service_name in self.last_scaling_action:
            elapsed = (datetime.now() - self.last_scaling_action[service_name]).total_seconds()
            if elapsed < self.policy.cooldown_seconds:
                return ScalingDecision(
                    action=ScalingAction.NO_ACTION,
                    current_instances=self.current_instances.get(service_name, 1),
                    target_instances=self.current_instances.get(service_name, 1),
                    reason=f"Cooldown active ({elapsed:.0f}s / {self.policy.cooldown_seconds}s)",
                    metrics=ResourceMetrics(0, 0, 0, 0, 0)
                )
        
        # Hole aktuelle Metriken
        if service_name not in self.metrics_history or not self.metrics_history[service_name]:
            return ScalingDecision(
                action=ScalingAction.NO_ACTION,
                current_instances=self.current_instances.get(service_name, 1),
                target_instances=self.current_instances.get(service_name, 1),
                reason="No metrics available",
                metrics=ResourceMetrics(0, 0, 0, 0, 0)
            )
        
        # Nutze letzte Metriken
        latest_metrics = self.metrics_history[service_name][-1]
        current_instances = self.current_instances.get(service_name, 1)
        
        # Berechne durchschnittliche CPU und Memory (letzte 5 Metriken)
        recent_metrics = self.metrics_history[service_name][-5:]
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        
        # Entscheide: Scale Up
        if avg_cpu > self.policy.scale_up_threshold or avg_memory > self.policy.scale_up_threshold:
            target_instances = min(
                current_instances + 1,
                self.policy.max_instances
            )
            if target_instances > current_instances:
                return ScalingDecision(
                    action=ScalingAction.SCALE_UP,
                    current_instances=current_instances,
                    target_instances=target_instances,
                    reason=f"High load: CPU={avg_cpu:.2f}, Memory={avg_memory:.2f}",
                    metrics=latest_metrics
                )
        
        # Entscheide: Scale Down
        if avg_cpu < self.policy.scale_down_threshold and avg_memory < self.policy.scale_down_threshold:
            target_instances = max(
                current_instances - 1,
                self.policy.min_instances
            )
            if target_instances < current_instances:
                return ScalingDecision(
                    action=ScalingAction.SCALE_DOWN,
                    current_instances=current_instances,
                    target_instances=target_instances,
                    reason=f"Low load: CPU={avg_cpu:.2f}, Memory={avg_memory:.2f}",
                    metrics=latest_metrics
                )
        
        # Keine Aktion
        return ScalingDecision(
            action=ScalingAction.NO_ACTION,
            current_instances=current_instances,
            target_instances=current_instances,
            reason=f"Load within thresholds: CPU={avg_cpu:.2f}, Memory={avg_memory:.2f}",
            metrics=latest_metrics
        )
    
    async def execute_scaling(self, service_name: str, decision: ScalingDecision) -> bool:
        """
        Führt Scaling aus
        
        Args:
            service_name: Service Name
            decision: Scaling Decision
        
        Returns:
            True wenn erfolgreich
        """
        if decision.action == ScalingAction.NO_ACTION:
            return True
        
        try:
            # TODO: Implementiere tatsächliche Scaling-Logik
            # - Docker/Kubernetes API
            # - Cloud Provider API (AWS, GCP, Azure)
            # - Service Discovery Update
            
            logger.info(
                f"Scaling {service_name}: {decision.current_instances} -> {decision.target_instances} "
                f"({decision.action.value}) - {decision.reason}"
            )
            
            # Update current instances
            self.current_instances[service_name] = decision.target_instances
            self.last_scaling_action[service_name] = datetime.now()
            
            # Hier würde die tatsächliche Scaling-Logik stehen
            # z.B.:
            # - Kubernetes: kubectl scale deployment {service_name} --replicas={target}
            # - Docker Swarm: docker service scale {service_name}={target}
            # - AWS ECS: Update service desired count
            # - etc.
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Scaling: {e}")
            return False
    
    async def monitor_and_scale(self, service_name: str):
        """
        Überwacht Service und skaliert automatisch
        
        Args:
            service_name: Service Name
        """
        while self.monitoring_enabled:
            try:
                decision = self.should_scale(service_name)
                
                if decision.action != ScalingAction.NO_ACTION:
                    await self.execute_scaling(service_name, decision)
                
                # Warte 60 Sekunden bis nächster Check
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Fehler beim Monitoring: {e}")
                await asyncio.sleep(60)


class CostOptimizer:
    """
    Cost Optimizer
    
    Optimiert Kosten durch intelligente Resource-Nutzung.
    """
    
    def __init__(self):
        """Initialisiert Cost Optimizer"""
        self.cost_history: Dict[str, List[float]] = {}  # service_name -> costs
    
    def calculate_cost(
        self,
        service_name: str,
        instances: int,
        cpu_hours: float,
        memory_gb_hours: float
    ) -> float:
        """
        Berechnet Kosten
        
        Args:
            service_name: Service Name
            instances: Anzahl Instanzen
            cpu_hours: CPU-Stunden
            memory_gb_hours: Memory GB-Stunden
        
        Returns:
            Kosten in USD
        """
        # Beispiel-Kosten (können konfiguriert werden)
        cpu_cost_per_hour = 0.10  # $0.10 pro CPU-Stunde
        memory_cost_per_gb_hour = 0.05  # $0.05 pro GB-Stunde
        
        total_cost = (cpu_hours * cpu_cost_per_hour) + (memory_gb_hours * memory_cost_per_gb_hour)
        
        # Speichere in History
        if service_name not in self.cost_history:
            self.cost_history[service_name] = []
        self.cost_history[service_name].append(total_cost)
        
        return total_cost
    
    def get_cost_recommendations(self, service_name: str) -> List[str]:
        """
        Gibt Cost-Optimierungs-Empfehlungen
        
        Args:
            service_name: Service Name
        
        Returns:
            Liste von Empfehlungen
        """
        recommendations = []
        
        if service_name not in self.cost_history:
            return recommendations
        
        costs = self.cost_history[service_name]
        if len(costs) < 2:
            return recommendations
        
        # Prüfe Trends
        recent_avg = sum(costs[-7:]) / len(costs[-7:]) if len(costs) >= 7 else sum(costs) / len(costs)
        older_avg = sum(costs[:-7]) / len(costs[:-7]) if len(costs) >= 14 else recent_avg
        
        if recent_avg > older_avg * 1.2:
            recommendations.append("Kosten sind um 20% gestiegen. Prüfe ob Scale-Down möglich ist.")
        
        if recent_avg < older_avg * 0.8:
            recommendations.append("Kosten sind gesunken. Gute Optimierung!")
        
        return recommendations


# Globale Instanzen
_global_auto_scaler: Optional[AutoScaler] = None
_global_cost_optimizer: Optional[CostOptimizer] = None


def get_auto_scaler(policy: Optional[ScalingPolicy] = None) -> AutoScaler:
    """Holt globale Auto-Scaler Instanz"""
    global _global_auto_scaler
    if _global_auto_scaler is None:
        _global_auto_scaler = AutoScaler(policy=policy)
    return _global_auto_scaler


def get_cost_optimizer() -> CostOptimizer:
    """Holt globale Cost Optimizer Instanz"""
    global _global_cost_optimizer
    if _global_cost_optimizer is None:
        _global_cost_optimizer = CostOptimizer()
    return _global_cost_optimizer
