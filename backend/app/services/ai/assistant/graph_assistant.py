"""Compatibility entry point for the AI chat API.

All chat requests are delegated to AssistantPipeline.  Legacy extractors,
planners, tool routing, and string context builders are intentionally not
constructed here.
"""

from typing import Optional

from app.services.ai.assistant.assistant_models import ChatRequest, ChatResponse
from app.services.ai.assistant.assistant_pipeline import AssistantPipeline
from app.services.ai.assistant.conversation.conversation_manager import ConversationManager
from app.services.ai.assistant.history.history_manager import HistoryManager
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.llm.config import settings
from app.services.ai.assistant.llm.ollama_provider import OllamaProvider
from app.services.ai.assistant.memory.memory_manager import MemoryManager
from app.services.ai.assistant.memory.memory_store import MemoryStore
from app.services.ai.assistant.memory.session_manager import SessionManager


class GraphAssistant:
    """Stable public façade for the unified assistant pipeline."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None, provider: Optional[BaseProvider] = None):
        self.memory = memory_manager or MemoryManager(MemoryStore())
        self.session_manager = SessionManager()
        self.history_manager = HistoryManager(self.memory.store)
        self.conversation = ConversationManager(self.memory, self.session_manager, self.history_manager)
        self.pipeline = AssistantPipeline(
            conversation=self.conversation,
            provider=provider or OllamaProvider(settings),
        )

    def chat(self, request: ChatRequest, stream: bool = False) -> ChatResponse:
        return self.pipeline.process(request, stream=stream)
