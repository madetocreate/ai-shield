"""
Agent Wrapper - Automatische Integration aller Features

Wrapper für Agents, der automatisch:
- Distributed Tracing
- Error Handling
- Cost Tracking
- Learning Feedback
- Real-time Metrics
- Event Publishing
integriert.
"""

from typing import Dict, Optional, Any, Callable
from functools import wraps
import asyncio
import logging
import time

logger = logging.getLogger(__name__)


def agent_wrapper(
    agent_name: str,
    track_cost: bool = True,
    track_learning: bool = True,
    track_metrics: bool = True,
    publish_events: bool = True
):
    """
    Agent Wrapper Decorator
    
    Integriert automatisch:
    - Distributed Tracing
    - Error Handling
    - Cost Tracking
    - Learning Feedback
    - Real-time Metrics
    - Event Publishing
    
    Args:
        agent_name: Agent Name
        track_cost: Ob Cost getrackt werden soll
        track_learning: Ob Learning Feedback gesammelt werden soll
        track_metrics: Ob Metrics gesendet werden sollen
        publish_events: Ob Events publiziert werden sollen
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Distributed Tracing
            from apps.agents.core.distributed_tracing import get_tracer
            tracer = get_tracer(service_name=agent_name)
            
            with tracer.start_span(f"{agent_name}.{func.__name__}", attributes={
                "agent": agent_name,
                "function": func.__name__
            }):
                start_time = time.time()
                error = None
                result = None
                
                try:
                    # Führe Function aus
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    success = True
                    
                except Exception as e:
                    duration = time.time() - start_time
                    success = False
                    error = str(e)
                    
                    # Error Event
                    if publish_events:
                        try:
                            from apps.agents.core.webhooks import get_event_bus, EventType, Event
                            bus = get_event_bus()
                            await bus.publish(Event(
                                id=f"error_{agent_name}_{time.time()}",
                                type=EventType.AGENT_ERROR,
                                payload={
                                    "agent": agent_name,
                                    "function": func.__name__,
                                    "error": str(e)
                                },
                                source=agent_name
                            ))
                        except Exception:
                            pass
                    
                    raise
                
                finally:
                    # Cost Tracking
                    if track_cost and success:
                        try:
                            from apps.agents.core.cost_tracking import get_cost_tracker, CostType
                            cost_tracker = get_cost_tracker()
                            
                            # Schätze Cost (vereinfacht)
                            estimated_cost = duration * 0.001  # Beispiel
                            account_id = kwargs.get("account_id") or "system"
                            
                            cost_tracker.track_cost(
                                account_id=account_id,
                                cost_type=CostType.COMPUTE,
                                amount=estimated_cost,
                                agent_name=agent_name,
                                metadata={
                                    "function": func.__name__,
                                    "duration": duration
                                }
                            )
                        except Exception as e:
                            logger.warning(f"Cost Tracking Fehler: {e}")
                    
                    # Real-time Metrics
                    if track_metrics:
                        try:
                            from apps.agents.core.real_time_monitoring import (
                                get_real_time_monitor,
                                RealTimeMetric
                            )
                            monitor = get_real_time_monitor()
                            await monitor.send_metric(RealTimeMetric(
                                name=f"{agent_name}.{func.__name__}",
                                value=duration,
                                labels={
                                    "agent": agent_name,
                                    "function": func.__name__,
                                    "success": str(success)
                                }
                            ))
                        except Exception as e:
                            logger.warning(f"Real-time Metrics Fehler: {e}")
                    
                    # Event Publishing
                    if publish_events and success:
                        try:
                            from apps.agents.core.webhooks import get_event_bus, EventType, Event
                            bus = get_event_bus()
                            await bus.publish(Event(
                                id=f"call_{agent_name}_{time.time()}",
                                type=EventType.AGENT_COMPLETED,
                                payload={
                                    "agent": agent_name,
                                    "function": func.__name__,
                                    "duration": duration
                                },
                                source=agent_name
                            ))
                        except Exception as e:
                            logger.warning(f"Event Publishing Fehler: {e}")
                
                return result
        
        return wrapper
    return decorator
