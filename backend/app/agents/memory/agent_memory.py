from typing import Dict, Any, List

class AgentMemory:
    """
    Local memory store for a specific agent. Used for caching domain-specific context
    and short-term reasoning traces.
    """
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._short_term: List[Dict[str, Any]] = []
        self._cache: Dict[str, Any] = {}

    def remember(self, event: Dict[str, Any]):
        self._short_term.append(event)
        # Prune if too large
        if len(self._short_term) > 100:
            self._short_term.pop(0)

    def set_cache(self, key: str, value: Any):
        self._cache[key] = value

    def get_cache(self, key: str) -> Any:
        return self._cache.get(key)
        
    def get_recent_history(self) -> List[Dict[str, Any]]:
        return self._short_term
