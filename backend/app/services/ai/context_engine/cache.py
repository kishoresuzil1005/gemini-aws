from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
import time

class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value or None if missing/expired."""
        ...

    @abstractmethod
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value with optional TTL (seconds)."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a cached entry."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached entries."""
        ...

class MemoryCache(CacheBackend):
    """Simple in‑memory cache with optional expiration timestamps."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}
        self._expirations: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        exp = self._expirations.get(key)
        if exp is not None and exp < time.time():
            # Expired – clean up and report miss
            self.delete(key)
            return None
        return self._store.get(key)

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = value
        if ttl:
            self._expirations[key] = time.time() + ttl
        elif key in self._expirations:
            del self._expirations[key]

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._expirations.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
        self._expirations.clear()
