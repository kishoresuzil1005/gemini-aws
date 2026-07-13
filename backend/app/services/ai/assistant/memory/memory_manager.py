from typing import Dict, Any, List
from app.services.ai.assistant.assistant_models import ConversationContext, Message
from app.services.ai.assistant.memory.memory_store import MemoryStore
from app.services.ai.assistant.memory.memory_search import MemorySearch
from app.services.ai.assistant.memory.memory_summary import MemorySummary

class MemoryManager:
    def __init__(self, store: MemoryStore):
        self.store = store
        self.searcher = MemorySearch(store)
        self.summarizer = MemorySummary()

    def add_message(self, session_id: str, role: str, content: str):
        self.store.append_message(session_id, Message(role=role, content=content))

    def get_context(self, session_id: str) -> ConversationContext:
        ctx_data = self.store.get_context(session_id)
        return ConversationContext(
            conversation_id=session_id,
            current_resource=ctx_data.get("current_resource"),
            current_intent=ctx_data.get("current_intent")
        )
        
    def update_context(self, session_id: str, updates: Dict[str, str]):
        ctx_data = self.store.get_context(session_id)
        ctx_data.update({k: v for k, v in updates.items() if v is not None})
        self.store.save_context(session_id, ctx_data)

    def search_memory(self, session_id: str, resource_name: str) -> List[Message]:
        return self.searcher.search_by_resource(session_id, resource_name)

    def summarize_memory(self, session_id: str) -> str:
        messages = self.store.get_messages(session_id)
        return self.summarizer.summarize_conversation(messages)

    def clear_history(self, session_id: str):
        self.store.clear(session_id)

    def get_history(self, session_id: str) -> List[Message]:
        return self.store.get_messages(session_id)