from typing import List
from app.services.ai.assistant.assistant_models import Message
from app.services.ai.assistant.memory.memory_store import MemoryStore

class HistoryManager:
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store

    def get_recent_history(self, session_id: str, limit: int = 5) -> List[Message]:
        history = self.store.get_messages(session_id)
        return history[-limit:] if history else []

    def get_full_history(self, session_id: str) -> List[Message]:
        return self.store.get_messages(session_id