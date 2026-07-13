from typing import Dict, Any

class MissionMemory:
    """
    Maintains the working context data specifically scoped to an active mission.
    """
    def __init__(self):
        self._contexts: Dict[str, Dict[str, Any]] = {}

    def set_context(self, mission_id: str, key: str, value: Any):
        if mission_id not in self._contexts:
            self._contexts[mission_id] = {}
        self._contexts[mission_id][key] = value

    def get_context(self, mission_id: str) -> Dict[str, Any]:
        return self._contexts.get(mission_id, {})

    def clear_context(self, mission_id: str):
        if mission_id in self._contexts:
            del self._contexts[mission_id