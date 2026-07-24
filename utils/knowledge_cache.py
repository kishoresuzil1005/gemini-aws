# utils/knowledge_cache.py
"""Simple in-memory LRU cache for Analyzer KS lookups."""
import time
from collections import OrderedDict
from typing import Any, Optional

class KnowledgeCache:
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self._store = OrderedDict()

    def _purge_expired(self):
        now = time.time()
        expired = [k for k, (v, exp) in self._store.items() if exp < now]
        for k in expired:
            self._store.pop(k, None)

    def get(self, key: str) -> Optional[Any]:
        self._purge_expired()
        if key not in self._store:
            return None
        val, exp = self._store.pop(key)
        self._store[key] = (val, exp)
        return val

    def set(self, key: str, value: Any):
        self._purge_expired()
        if key in self._store:
            self._store.pop(key)
        elif len(self._store) >= self.max_size:
            self._store.popitem(last=False)
        self._store[key] = (value, time.time() + self.ttl)
