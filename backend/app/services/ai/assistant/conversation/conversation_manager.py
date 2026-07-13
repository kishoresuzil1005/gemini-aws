from typing import Dict, Any
from app.services.ai.assistant.memory.memory_manager import MemoryManager
from app.services.ai.assistant.memory.session_manager import SessionManager
from app.services.ai.assistant.history.history_manager import HistoryManager
from app.services.ai.assistant.history.history_formatter import HistoryFormatter
from app.services.ai.assistant.assistant_models import ConversationContext

class ConversationManager:
    def __init__(self, memory: MemoryManager, session_manager: SessionManager, history_manager: HistoryManager):
        self.memory = memory
        self.session_manager = session_manager
        self.history = history_manager
        self.formatter = HistoryFormatter()

    def process_turn(self, session_id: str, current_intent_data: Dict[str, Any]) -> ConversationContext:
        """
        Processes a conversation turn, updating memory context, persisting session state,
        and handling resource context carry-over.
        """
        ctx = self.memory.get_context(session_id)
        
        # Resolve 'it' or carry over resource
        new_resource = current_intent_data.get("target_resource")
        if new_resource:
            self.memory.update_context(session_id, {"current_resource": new_resource})
        else:
            current_intent_data["target_resource"] = ctx.current_resource
            
        new_intent = current_intent_data.get("intent")
        if new_intent and new_intent != "UNKNOWN":
            self.memory.update_context(session_id, {
                "current_intent": new_intent,
                "last_intent": ctx.current_intent if ctx.current_intent else "UNKNOWN"
            })
        else:
            current_intent_data["intent"] = ctx.current_intent if ctx.current_intent else "UNKNOWN"
            
        return self.memory.get_context(session_id)

    def get_formatted_history(self, session_id: str, limit: int = 5) -> str:
        messages = self.history.get_recent_history(session_id, limit)
        # We might not want the very last message in history if it's the current prompt
        if messages:
            messages = messages[:-1]
        return self.formatter.format_for_prompt(messages)