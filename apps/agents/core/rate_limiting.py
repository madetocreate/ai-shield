"""
Rate Limiting - Rate Limiting für Agent-System

Implementiert:
- Rate Limiting pro Account
- Rate Limiting pro Agent
- Rate Limiting pro User
- Sliding Window Algorithm
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import time

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

import os


@dataclass
class RateLimitConfig:
    """Rate Limit Konfiguration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10  # Erlaubte Burst-Anfragen


@dataclass
class RateLimitResult:
    """Rate Limit Ergebnis"""
    allowed: bool
    remaining: int
    reset_at: datetime
    limit: int
    retry_after: Optional[int] = None  # Sekunden bis Reset


class RateLimiter:
    """
    Rate Limiter für Agent-System
    
    Nutzt Redis (falls verfügbar) oder In-Memory für Rate Limiting.
    """
    
    def __init__(self, redis_client=None):
        """
        Initialisiert Rate Limiter
        
        Args:
            redis_client: Redis Client (optional)
        """
        self.redis_client = redis_client
        self.memory_store: Dict[str, list] = defaultdict(list)  # key -> [timestamps]
        
        if not self.redis_client and REDIS_AVAILABLE:
            try:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", 6379))
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=1,  # DB 1 für Rate Limiting
                    decode_responses=False
                )
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
                print("WARNING: Redis nicht verfügbar, nutze In-Memory Rate Limiting")
    
    def check_rate_limit(
        self,
        key: str,
        config: RateLimitConfig,
        window_seconds: int = 60
    ) -> RateLimitResult:
        """
        Prüft Rate Limit
        
        Args:
            key: Eindeutiger Key (z.B. "account:123" oder "user:456")
            config: Rate Limit Konfiguration
            window_seconds: Zeitfenster in Sekunden (default: 60 für pro Minute)
        
        Returns:
            RateLimitResult
        """
        now = datetime.now()
        limit = config.requests_per_minute if window_seconds == 60 else config.requests_per_hour
        
        # Redis
        if self.redis_client:
            return self._check_redis(key, limit, window_seconds, now)
        
        # Memory
        return self._check_memory(key, limit, window_seconds, now)
    
    def _check_redis(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        now: datetime
    ) -> RateLimitResult:
        """Prüft Rate Limit mit Redis"""
        try:
            redis_key = f"ratelimit:{key}:{window_seconds}"
            current = self.redis_client.get(redis_key)
            
            if current is None:
                # Erster Request in diesem Fenster
                self.redis_client.setex(redis_key, window_seconds, 1)
                reset_at = now + timedelta(seconds=window_seconds)
                return RateLimitResult(
                    allowed=True,
                    remaining=limit - 1,
                    reset_at=reset_at,
                    limit=limit
                )
            
            count = int(current)
            
            if count >= limit:
                # Rate Limit überschritten
                ttl = self.redis_client.ttl(redis_key)
                reset_at = now + timedelta(seconds=ttl)
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=reset_at,
                    limit=limit,
                    retry_after=ttl
                )
            
            # Erhöhe Counter
            self.redis_client.incr(redis_key)
            reset_at = now + timedelta(seconds=self.redis_client.ttl(redis_key))
            
            return RateLimitResult(
                allowed=True,
                remaining=limit - count - 1,
                reset_at=reset_at,
                limit=limit
            )
            
        except Exception as e:
            print(f"Redis Rate Limit Error: {e}, fallback zu Memory")
            return self._check_memory(key, limit, window_seconds, now)
    
    def _check_memory(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        now: datetime
    ) -> RateLimitResult:
        """Prüft Rate Limit mit Memory"""
        window_start = now - timedelta(seconds=window_seconds)
        
        # Entferne alte Timestamps
        timestamps = self.memory_store[key]
        timestamps[:] = [ts for ts in timestamps if ts > window_start]
        
        # Prüfe Limit
        if len(timestamps) >= limit:
            # Rate Limit überschritten
            oldest = min(timestamps)
            reset_at = oldest + timedelta(seconds=window_seconds)
            retry_after = int((reset_at - now).total_seconds())
            
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=reset_at,
                limit=limit,
                retry_after=max(0, retry_after)
            )
        
        # Erlaubt
        timestamps.append(now)
        reset_at = now + timedelta(seconds=window_seconds)
        
        return RateLimitResult(
            allowed=True,
            remaining=limit - len(timestamps),
            reset_at=reset_at,
            limit=limit
        )
    
    def check_account_limit(
        self,
        account_id: str,
        config: Optional[RateLimitConfig] = None
    ) -> RateLimitResult:
        """Prüft Rate Limit für Account"""
        config = config or RateLimitConfig()
        key = f"account:{account_id}"
        return self.check_rate_limit(key, config, window_seconds=60)
    
    def check_agent_limit(
        self,
        agent_name: str,
        account_id: str,
        config: Optional[RateLimitConfig] = None
    ) -> RateLimitResult:
        """Prüft Rate Limit für Agent"""
        config = config or RateLimitConfig()
        key = f"agent:{account_id}:{agent_name}"
        return self.check_rate_limit(key, config, window_seconds=60)
    
    def check_user_limit(
        self,
        user_id: str,
        account_id: str,
        config: Optional[RateLimitConfig] = None
    ) -> RateLimitResult:
        """Prüft Rate Limit für User"""
        config = config or RateLimitConfig()
        key = f"user:{account_id}:{user_id}"
        return self.check_rate_limit(key, config, window_seconds=60)


# Globale Rate Limiter-Instanz
_global_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Holt globale Rate Limiter-Instanz"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter()
    return _global_rate_limiter
