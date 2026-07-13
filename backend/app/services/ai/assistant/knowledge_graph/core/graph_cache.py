from typing import Dict, Any

class GraphCache:
    """Memory caching for heavy topology structures."""
    
    def __init__(self):
        self._cache = {}
        
    def get(self, key: str) -> Any:
        return self._cache.get(key)
        
    def set(self, key: str, value: Any):
        self._cache[key] = valu