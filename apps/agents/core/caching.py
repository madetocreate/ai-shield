"""
Caching - Performance-Optimierung für Intent & Routing

Cached:
- Intent-Erkennung (ähnliche Nachrichten)
- Routing-Entscheidungen
- Agent-Responses (optional)
"""

from typing import Optional, Any, Dict, Callable
from functools import wraps
import hashlib
import json
import time
import os

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class Cache:
    """
    Cache für Agent-System
    
    Nutzt Redis (falls verfügbar) oder In-Memory Cache.
    """
    
    def __init__(self, redis_client=None, default_ttl: int = 300):
        """
        Initialisiert Cache
        
        Args:
            redis_client: Redis Client (optional)
            default_ttl: Default TTL in Sekunden
        """
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, tuple] = {}  # key -> (value, expires_at)
        
        if not self.redis_client and REDIS_AVAILABLE:
            try:
                # Versuche Redis zu verbinden
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", 6379))
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=0,
                    decode_responses=True
                )
                # Test Connection
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
                print("WARNING: Redis nicht verfügbar, nutze In-Memory Cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Holt Wert aus Cache"""
        # Redis
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception:
                pass
        
        # Memory Cache
        if key in self.memory_cache:
            value, expires_at = self.memory_cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Setzt Wert in Cache"""
        ttl = ttl or self.default_ttl
        
        # Redis
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, ensure_ascii=False)
                )
                return
            except Exception:
                pass
        
        # Memory Cache
        expires_at = time.time() + ttl
        self.memory_cache[key] = (value, expires_at)
    
    def delete(self, key: str):
        """Löscht Wert aus Cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                pass
        
        if key in self.memory_cache:
            del self.memory_cache[key]
    
    def clear(self):
        """Löscht gesamten Cache"""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception:
                pass
        
        self.memory_cache.clear()


def cache_key(*args, **kwargs) -> str:
    """Generiert Cache-Key aus Arguments"""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(key_str.encode()).hexdigest()


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Cache Decorator
    
    Args:
        ttl: Time to Live in Sekunden
        key_func: Custom Key-Funktion
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generiere Cache-Key
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Prüfe Cache
            cache = get_cache()
            cached_value = cache.get(cache_key_str)
            
            if cached_value is not None:
                return cached_value
            
            # Führe Function aus
            result = func(*args, **kwargs)
            
            # Speichere in Cache
            cache.set(cache_key_str, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Globale Cache-Instanz
_global_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Holt globale Cache-Instanz"""
    global _global_cache
    if _global_cache is None:
        _global_cache = Cache()
    return _global_cache


# Import für os
import os
