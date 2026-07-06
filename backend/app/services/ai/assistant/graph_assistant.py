from typing import Dict, Any
from app.services.ai.assistant.memory_manager import MemoryManager
from app.services.ai.assistant.intent_classifier import IntentClassifier
from app.services.ai.assistant.context_builder import ContextBuilder
from app.services.ai.assistant.response_generator import ResponseGenerator
from app.services.ai.assistant.llm_provider import MockLLMProvider

class GraphAssistant:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.classifier = IntentClassifier()
        self.context_builder = ContextBuilder()
        self.generator = ResponseGenerator(MockLLMProvider())

    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        # 1. Add to Memory
        self.memory.add_message(session_id, "user", message)
        
        # 2. Intent Detection
        intent_data = self.classifier.classify(message)
        
        # Resolve target resource from context if missing
        if not intent_data.get("target_resource"):
            saved_target = self.memory.get_context(session_id).get("target_resource")
            if saved_target:
                intent_data["target_resource"] = saved_target
        elif intent_data.get("target_resource"):
            self.memory.update_context(session_id, "target_resource", intent_data["target_resource"])
            
        # 3. Context Building
        context_str = self.context_builder.build_context(intent_data)
        
        # 4. History formatting
        history = self.memory.get_history(session_id)
        # Convert history to simple string for prompt
        history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history[-5:]]) # last 5 turns
        
        # 5. Response Generation
        response_text = self.generator.generate(message, history_str, context_str)
        
        # 6. Save assistant response
        self.memory.add_message(session_id, "assistant", response_text)
        
        return {
            "response": response_text,
            "intent": intent_data.get("intent"),
            "target": intent_data.get("target_resource")
        }
