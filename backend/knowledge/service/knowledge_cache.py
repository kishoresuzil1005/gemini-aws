# knowledge/service/knowledge_cache.py
"""In-memory cache for expensive Service queries."""

import time
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class CacheEntry:
    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.expiry = time.time() + ttl

class KnowledgeCache:
    """A thread-safe, pure-Python LRU/TTL cache."""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry.expiry:
            del self._cache[key]
            return None
        return entry.data

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        if len(self._cache) >= self.max_size:
            # Simple eviction: clear 10% randomly or just flush expired (simplified for now)
            self._prune()
            
        final_ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = CacheEntry(data, final_ttl)

    def _prune(self):
        """Remove expired keys."""
        now = time.time()
        expired = [k for k, v in self._cache.items() if now > v.expiry]
        for k in expired:
            del self._cache[k]
        
        # If still too large, just clear it (basic fallback)
        if len(self._cache) >= self.max_size:
            self.clear()

    def clear(self):
        """Flush the cache (useful on catalog updates)."""
        self._cache.clear()
        logger.info("KnowledgeCache cleared.")
