from typing import Dict, Any, Optional
import time

class ProviderCacheManager:
    """Manages caching of provider responses and metrics."""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and time.time() < entry['expiry']:
            return entry['value']
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._cache[key] = {
            'value': value,
            'expiry': time.time() + ttl_seconds
        }
