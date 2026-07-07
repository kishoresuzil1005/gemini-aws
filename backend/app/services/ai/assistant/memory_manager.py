from typing import List, Dict
from app.services.ai.assistant.assistant_models import ConversationContext, Message

class MemoryManager:
    def __init__(self):
        self._history: Dict[str, List[Message]] = {}
        self._contexts: Dict[str, ConversationContext] = {}

    def add_message(self, conversation_id: str, role: str, content: str):
        if conversation_id not in self._history:
            self._history[conversation_id] = []
        self._history[conversation_id].append(Message(role=role, content=content))

    def get_history(self, conversation_id: str) -> List[Message]:
        return self._history.get(conversation_id, [])

    def clear_history(self, conversation_id: str):
        if conversation_id in self._history:
            self._history[conversation_id] = []
        if conversation_id in self._contexts:
            self._contexts[conversation_id] = ConversationContext(conversation_id=conversation_id)

    def get_context(self, conversation_id: str) -> ConversationContext:
        if conversation_id not in self._contexts:
            self._contexts[conversation_id] = ConversationContext(conversation_id=conversation_id)
        return self._contexts[conversation_id]
        
    def update_context(self, conversation_id: str, updates: Dict[str, str]):
        ctx = self.get_context(conversation_id)
        for key, value in updates.items():
            if hasattr(ctx, key) and value is not None:
                setattr(ctx, key, value)
