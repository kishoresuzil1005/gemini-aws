"""
Orchestrator Cache (Phase 7 / Phase 4)
========================================
Thin wrapper around Redis for session caching of resolved resources
and unified context objects.  Falls back gracefully when Redis is
unavailable (unit-test / offline mode).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 1800  # 30 minutes


def _get_redis():
    """Lazy Redis connection — returns None if unavailable."""
    try:
        import redis
        import os
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        client = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=1)
        client.ping()
        return client
    except Exception as e:
        logger.debug("[Cache] Redis unavailable (%s) — running without cache", e)
        return None


class OrchestratorCache:
    """
    Key-value cache for orchestrator data.

    Keys follow the pattern:
      - resolved:<session_id>:<query_hash>   → ResolvedResource JSON
      - context:<session_id>                 → UnifiedContext JSON
      - investigation:<session_id>           → Investigation session JSON
    """

    def __init__(self, ttl: int = _DEFAULT_TTL):
        self._ttl = ttl
        self._redis = _get_redis()
        self._fallback: dict = {}  # in-memory fallback

    # ------------------------------------------------------------------
    def get(self, key: str) -> Optional[Any]:
        if self._redis:
            try:
                raw = self._redis.get(key)
                if raw:
                    return json.loads(raw)
            except Exception as e:
                logger.warning("[Cache] GET error: %s", e)
        return self._fallback.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self._ttl
        serialised = json.dumps(value, default=str)
        if self._redis:
            try:
                self._redis.setex(key, ttl, serialised)
                return
            except Exception as e:
                logger.warning("[Cache] SET error: %s", e)
        self._fallback[key] = json.loads(serialised)

    def delete(self, key: str) -> None:
        if self._redis:
            try:
                self._redis.delete(key)
            except Exception as e:
                logger.warning("[Cache] DELETE error: %s", e)
        self._fallback.pop(key, None)

    def is_available(self) -> bool:
        return self._redis is not None
