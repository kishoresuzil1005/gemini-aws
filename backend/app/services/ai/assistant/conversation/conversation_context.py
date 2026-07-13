from typing import Dict, Any
from .conversation_history import ConversationHistory

class ConversationContext:
    """
    Maintains rich session-level context beyond raw messages:
    active cloud account, active mission, current intent, etc.
    """
    def __init__(self):
        self._context: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._context)

    def reset(self):
        self._context = {