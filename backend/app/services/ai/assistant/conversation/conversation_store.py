from typing import Dict, Any, Optional

class ConversationStore:
    def __init__(self):
        # In-memory store for now
        self._store: Dict[str, Dict[str, Any]] = {}

    def save_conversation(self, conversation_id: str, data: Dict[str, Any]):
        self._store[conversation_id] = data

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(conversation_id)

    def delete_conversation(self, conversation_id: str):
        if conversation_id in self._store:
            del self._store[conversation_id]
