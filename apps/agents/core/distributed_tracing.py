"""
Distributed Tracing - OpenTelemetry Integration

Features:
- End-to-End Tracing
- Performance Analysis
- Dependency Mapping
- Error Tracking
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.warning("OpenTelemetry nicht verfügbar. Installiere: pip install opentelemetry-api opentelemetry-sdk")


@dataclass
class Span:
    """Span (vereinfacht wenn OpenTelemetry nicht verfügbar)"""
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    error: Optional[str] = None


class DistributedTracer:
    """
    Distributed Tracer
    
    Verwaltet Traces für End-to-End Request-Tracking.
    """
    
    def __init__(self, service_name: str = "ai-shield-agents"):
        """
        Initialisiert Distributed Tracer
        
        Args:
            service_name: Service Name
        """
        self.service_name = service_name
        self.tracer = None
        
        if OPENTELEMETRY_AVAILABLE:
            self._setup_opentelemetry()
        else:
            logger.warning("OpenTelemetry nicht verfügbar, nutze vereinfachtes Tracing")
            self.spans: List[Span] = []
    
    def _setup_opentelemetry(self):
        """Setzt OpenTelemetry auf"""
        try:
            # Tracer Provider
            provider = TracerProvider()
            trace.set_tracer_provider(provider)
            
            # Span Exporter (kann konfiguriert werden)
            otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
            if otlp_endpoint:
                exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            else:
                exporter = ConsoleSpanExporter()
            
            provider.add_span_processor(BatchSpanProcessor(exporter))
            
            self.tracer = trace.get_tracer(self.service_name)
            logger.info("OpenTelemetry Tracer initialisiert")
        except Exception as e:
            logger.error(f"Fehler beim Setup von OpenTelemetry: {e}")
            self.tracer = None
    
    @contextmanager
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Startet Span (Context Manager)
        
        Args:
            name: Span Name
            attributes: Span Attributes
        """
        if self.tracer:
            # OpenTelemetry
            span = self.tracer.start_as_current_span(name)
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            finally:
                span.end()
        else:
            # Vereinfachtes Tracing
            span = Span(
                name=name,
                start_time=datetime.now(),
                attributes=attributes or {}
            )
            try:
                yield span
            except Exception as e:
                span.status = "error"
                span.error = str(e)
                raise
            finally:
                span.end_time = datetime.now()
                self.spans.append(span)
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Fügt Event zu aktuellem Span hinzu"""
        if self.tracer:
            span = trace.get_current_span()
            if span:
                span.add_event(name, attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """Setzt Attribute für aktuellem Span"""
        if self.tracer:
            span = trace.get_current_span()
            if span:
                span.set_attribute(key, str(value))
    
    def get_trace_id(self) -> Optional[str]:
        """Holt Trace ID"""
        if self.tracer:
            span = trace.get_current_span()
            if span:
                return format(span.get_span_context().trace_id, '032x')
        return None


# Globale Tracer-Instanz
_global_tracer: Optional[DistributedTracer] = None


def get_tracer(service_name: str = "ai-shield-agents") -> DistributedTracer:
    """Holt globale Tracer-Instanz"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = DistributedTracer(service_name=service_name)
    return _global_tracer


import os
