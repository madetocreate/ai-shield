"""
Error Handling & Retry Logic - Production-Ready Error Handling

Implementiert:
- Retry Logic mit Exponential Backoff
- Circuit Breaker Pattern
- Graceful Degradation
- Error Recovery
"""

from typing import Callable, Optional, Any, TypeVar, Dict
from functools import wraps
import time
import asyncio
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

T = TypeVar('T')


class ErrorCategory(str, Enum):
    """Error-Kategorien"""
    TRANSIENT = "transient"  # Vorübergehend, Retry sinnvoll
    PERMANENT = "permanent"  # Dauerhaft, kein Retry
    RATE_LIMIT = "rate_limit"  # Rate Limit, Retry mit Backoff
    TIMEOUT = "timeout"  # Timeout, Retry sinnvoll
    AUTHENTICATION = "authentication"  # Auth-Fehler, kein Retry


@dataclass
class RetryConfig:
    """Retry-Konfiguration"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerState:
    """Circuit Breaker State"""
    failures: int = 0
    last_failure: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    opened_at: Optional[datetime] = None


class CircuitBreaker:
    """
    Circuit Breaker Pattern
    
    Verhindert wiederholte Calls zu fehlerhaften Services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.state = CircuitBreakerState()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Führt Function mit Circuit Breaker aus"""
        if self.state.state == "open":
            # Prüfe ob Timeout abgelaufen
            if self.state.opened_at:
                elapsed = (datetime.now() - self.state.opened_at).total_seconds()
                if elapsed > self.timeout:
                    # Versuche Half-Open
                    self.state.state = "half_open"
                    self.state.failures = 0
                else:
                    raise Exception("Circuit Breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            # Erfolg
            if self.state.state == "half_open":
                self.state.failures += 1
                if self.state.failures >= self.success_threshold:
                    # Zurück zu Closed
                    self.state.state = "closed"
                    self.state.failures = 0
                    self.state.opened_at = None
            
            return result
            
        except Exception as e:
            # Fehler
            self.state.failures += 1
            self.state.last_failure = datetime.now()
            
            if self.state.failures >= self.failure_threshold:
                # Öffne Circuit Breaker
                self.state.state = "open"
                self.state.opened_at = datetime.now()
            
            raise


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    retry_on: Optional[list] = None
):
    """
    Retry Decorator mit Exponential Backoff
    
    Args:
        config: Retry-Konfiguration
        retry_on: Exception-Typen die retried werden sollen
    """
    if config is None:
        config = RetryConfig()
    
    if retry_on is None:
        retry_on = [Exception]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except tuple(retry_on) as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        # Berechne Delay
                        delay = min(
                            config.initial_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        
                        # Jitter hinzufügen
                        if config.jitter:
                            import random
                            delay = delay * (0.5 + random.random() * 0.5)
                        
                        time.sleep(delay)
                    else:
                        # Letzter Versuch fehlgeschlagen
                        raise
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def graceful_degradation(
    fallback_func: Optional[Callable] = None,
    fallback_value: Any = None
):
    """
    Graceful Degradation Decorator
    
    Falls Function fehlschlägt, nutze Fallback.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Function {func.__name__} failed: {e}, using fallback")
                
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                else:
                    return fallback_value
        
        return wrapper
    return decorator


class ErrorHandler:
    """
    Zentrale Error Handling-Klasse
    
    Kategorisiert Fehler und wählt passende Strategie.
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Holt oder erstellt Circuit Breaker für Service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """Kategorisiert Error"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            return ErrorCategory.RATE_LIMIT
        
        if "timeout" in error_str or "timed out" in error_str:
            return ErrorCategory.TIMEOUT
        
        if "auth" in error_str or "401" in error_str or "403" in error_str:
            return ErrorCategory.AUTHENTICATION
        
        # Transient Errors (5xx)
        if "500" in error_str or "502" in error_str or "503" in error_str:
            return ErrorCategory.TRANSIENT
        
        # Default: Permanent
        return ErrorCategory.PERMANENT
    
    def should_retry(self, error: Exception, attempt: int, max_attempts: int) -> bool:
        """Prüft ob Retry sinnvoll ist"""
        if attempt >= max_attempts:
            return False
        
        category = self.categorize_error(error)
        
        return category in [
            ErrorCategory.TRANSIENT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.TIMEOUT
        ]


# Globale Error Handler-Instanz
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Holt globale Error Handler-Instanz"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler
