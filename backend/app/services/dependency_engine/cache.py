import threading
from typing import Any, Optional

class DependencyCache:
    """Thread-safe cache for dependency queries to improve performance."""
    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = value

    def invalidate(self, key: str):
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        with self._lock:
            self._cache.clear()
