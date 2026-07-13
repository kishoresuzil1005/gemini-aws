from typing import List, Dict, Any
from app.services.ai.assistant.assistant_models import Message

class MemorySearch:
    def __init__(self, memory_store):
        self.store = memory_store

    def search_by_resource(self, session_id: str, resource_name: str) -> List[Message]:
        """
        Retrieves memory related to a specific resource.
        """
        history = self.store.get_messages(session_id)
        # Basic keyword search for now
        return [msg for msg in history if resource_name in msg.content