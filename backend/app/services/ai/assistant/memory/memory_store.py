from typing import List, Dict, Any, Optional
from app.services.ai.assistant.assistant_models import Message

class MemoryStore:
    def __init__(self):
        # In-memory store for memory items
        self._history: Dict[str, List[Message]] = {}
        self._context: Dict[str, Dict[str, Any]] = {}

    def append_message(self, session_id: str, message: Message):
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append(message)

    def get_messages(self, session_id: str) -> List[Message]:
        return self._history.get(session_id, [])

    def save_context(self, session_id: str, context: Dict[str, Any]):
        self._context[session_id] = context

    def get_context(self, session_id: str) -> Dict[str, Any]:
        return self._context.get(session_id, {})
        
    def clear(self, session_id: str):
        if session_id in self._history:
            del self._history[session_id]
        if session_id in self._context:
            del self._context[session_id]