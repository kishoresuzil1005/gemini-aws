from typing import Dict, Any
from app.services.ai.assistant.memory_manager import MemoryManager
from app.services.ai.assistant.assistant_models import ConversationContext

class ConversationManager:
    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def process_turn(self, conversation_id: str, current_intent_data: Dict[str, Any]) -> ConversationContext:
        ctx = self.memory.get_context(conversation_id)
        
        # If the user didn't specify a resource this turn, carry it over from memory
        new_resource = current_intent_data.get("target_resource")
        if new_resource:
            self.memory.update_context(conversation_id, {"current_resource": new_resource})
        else:
            current_intent_data["target_resource"] = ctx.current_resource
            
        new_intent = current_intent_data.get("intent")
        if new_intent and new_intent != "UNKNOWN":
            self.memory.update_context(conversation_id, {"current_intent": new_intent})
        else:
            current_intent_data["intent"] = ctx.current_intent if ctx.current_intent else "UNKNOWN"
            
        return self.memory.get_context(conversation_id)
