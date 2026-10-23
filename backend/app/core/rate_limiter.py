import time
from typing import Dict, List, Optional

import redis.asyncio as aioredis
from app.core.config import settings
from app.core.errors import RateLimitExceededError
from app.core.logging import logger


class RateLimiter:
    """
    Sliding window rate limiter supporting Redis with an in-memory fallback.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis_client: Optional[aioredis.Redis] = None
        self._memory_store: Dict[str, List[float]] = {}

    async def get_redis(self) -> Optional[aioredis.Redis]:
        if self._redis_client is None:
            try:
                client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1.0,
                    socket_timeout=1.0,
                )
                await client.ping()
                self._redis_client = client
            except Exception as e:
                logger.debug(f"Redis unavailable for rate limiter; using in-memory store: {e}")
                self._redis_client = None
        return self._redis_client

    async def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Returns True if within limit, raises RateLimitExceededError if exceeded.
        """
        now = time.time()
        client = await self.get_redis()

        if client:
            try:
                pipe = client.pipeline()
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, window_seconds)
                results = await pipe.execute()
                current_count = results[2]
                if current_count > max_requests:
                    raise RateLimitExceededError(
                        f"Rate limit exceeded. Maximum {max_requests} requests allowed per {window_seconds}s."
                    )
                return True
            except (RateLimitExceededError, Exception) as exc:
                if isinstance(exc, RateLimitExceededError):
                    raise
                logger.warning(f"Redis error during rate limiting, falling back to memory: {exc}")

        # In-memory sliding window fallback
        timestamps = self._memory_store.get(key, [])
        valid_timestamps = [t for t in timestamps if t > now - window_seconds]
        if len(valid_timestamps) >= max_requests:
            self._memory_store[key] = valid_timestamps
            raise RateLimitExceededError(
                f"Rate limit exceeded. Maximum {max_requests} requests allowed per {window_seconds}s."
            )
        valid_timestamps.append(now)
        self._memory_store[key] = valid_timestamps
        return True


rate_limiter = RateLimiter()
