
import json
import logging
import time
from typing import Any, Optional, Dict
from backend.app.core.config import settings

logger = logging.getLogger("LegionEngine")

class CacheService:
    """
    Unified Caching Layer for the Legion Engine.
    Handles Local In-Memory caching (development) and Redis (production).
    """
    _instance = None
    _memory_cache: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.redis = None
        # 1. Determine the best connection URL
        url = settings.redis_url
        
        # If no direct REDIS_URL, check for Upstash specific REST keys 
        # (Though redis-py usually needs the rediss:// connection string)
        if not url and settings.upstash_redis_rest_url:
            # Note: Upstash REST URL starts with https://, we need redis:// for this lib
            # Most users also have a REDIS_URL provided by Upstash.
            logger.warning("CacheService: UPSTASH_REDIS_REST_URL found but redis-py requires a redis:// or rediss:// connection string.")

        if settings.enable_redis_cache and url:
            try:
                import redis
                self.redis = redis.from_url(url, decode_responses=True)
                logger.info("CacheService: Redis Connection Active")
            except ImportError:
                logger.warning("CacheService: redis-py not installed. Falling back to Memory.")
            except Exception as e:
                logger.error(f"CacheService: Redis Connection Failed: {e}")
        elif settings.enable_redis_cache:
            logger.warning("CacheService: Redis enabled but no REDIS_URL provided. Falling back to Memory.")

    def get(self, key: str) -> Optional[Any]:
        """Fetch a value from the cache."""
        # 1. Try Redis
        if self.redis:
            try:
                val = self.redis.get(key)
                return json.loads(val) if val else None
            except Exception as e:
                logger.error(f"CacheService (Redis) Get Error: {e}")

        # 2. Try Memory
        entry = self._memory_cache.get(key)
        if entry:
            if time.time() < entry["expiry"]:
                return entry["value"]
            else:
                del self._memory_cache[key] # Cleanup expired
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Store a value in the cache.
        :param ttl: Time-To-Live in seconds (default 5 minutes)
        """
        # 1. Set in Redis
        if self.redis:
            try:
                self.redis.set(key, json.dumps(value), ex=ttl)
            except Exception as e:
                logger.error(f"CacheService (Redis) Set Error: {e}")

        # 2. Set in Memory
        self._memory_cache[key] = {
            "value": value,
            "expiry": time.time() + ttl
        }

    def delete(self, key: str):
        """Remove a specific key."""
        if self.redis:
            try:
                self.redis.delete(key)
            except Exception as e:
                logger.error(f"CacheService (Redis) Delete Error: {e}")
        
        if key in self._memory_cache:
            del self._memory_cache[key]

    def delete_pattern(self, pattern: str):
        """Invalidate all keys matching a pattern (e.g., 'world:state:*')"""
        # Note: In-memory pattern matching is simple prefix matching here
        if self.redis:
            try:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            except Exception as e:
                logger.error(f"CacheService (Redis) Pattern Delete Error: {e}")

        # Memory cleanup
        prefix = pattern.replace("*", "")
        keys_to_del = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            del self._memory_cache[k]

cache_service = CacheService()
