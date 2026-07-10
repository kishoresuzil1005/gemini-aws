import time
from typing import Dict, Any, Optional

class ProviderCache:
    """Caches Regions, Resource Metadata, Quotas, SKUs to avoid repeated API calls."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }
        
    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None
            
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
            
        return entry["value"]

# Global cache instance
provider_cache = ProviderCache()
