from typing import Dict, Any, Optional

class SharedMemory:
    """
    A globally accessible state store used by the platform to coordinate long-running state 
    across multiple agents.
    """
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def write(self, key: str, value: Any):
        self._store[key] = value

    def read(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def append_to_list(self, key: str, value: Any):
        if key not in self._store:
            self._store[key] = []
        if isinstance(self._store[key], list):
            self._store[key].append(value)
