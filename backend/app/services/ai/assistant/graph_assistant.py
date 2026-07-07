from typing import Dict, Any, List
from app.services.ai.assistant.memory_manager import MemoryManager
from app.services.ai.assistant.conversation_manager import ConversationManager
from app.services.ai.assistant.intent_classifier import IntentClassifier
from app.services.ai.assistant.tool_router import ToolRouter
from app.services.ai.assistant.context_builder import ContextBuilder
from app.services.ai.assistant.response_generator import ResponseGenerator
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.llm.ollama_provider import OllamaProvider
from app.services.ai.assistant.llm.config import settings
import uuid
from app.services.ai.assistant.assistant_models import ChatResponse, ChatRequest

class GraphAssistant:
    def __init__(self, memory_manager: MemoryManager, provider: BaseProvider = None):
        self.memory = memory_manager
        self.conversation = ConversationManager(memory_manager)
        self.classifier = IntentClassifier()
        self.tool_router = ToolRouter()
        self.context_builder = ContextBuilder()
        self.provider = provider or OllamaProvider(settings)
        self.generator = ResponseGenerator(self.provider)

    def chat(self, request: ChatRequest, stream: bool = False) -> ChatResponse:
        request_id = str(uuid.uuid4())
        print(f"[Req: {request_id}] Starting AI Chat for Conversation: {request.conversation_id}")
        
        # 1. Add to Memory
        self.memory.add_message(request.conversation_id, "user", request.message)
        
        # 2. Intent Classification
        intent_data = self.classifier.classify(request.message)
        
        # 3. Conversation Context Processing
        ctx = self.conversation.process_turn(request.conversation_id, intent_data)
        
        # 4. Tool Execution
        tool_responses = []
        if ctx.current_intent != "UNKNOWN":
            tr = self.tool_router.route(ctx.current_intent, ctx.current_resource)
            tool_responses.append(tr)
            
        # 5. Context Building
        context_str = self.context_builder.build_structured_context(ctx, tool_responses)
        
        # 6. History formatting
        history = self.memory.get_history(request.conversation_id)
        # Avoid passing the last message again as it is passed as the current question
        history_str = "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in history[-6:-1]]) 
        
        # 7. Response Generation
        chat_response = self.generator.generate(
            question=request.message,
            history_str=history_str,
            context_str=context_str,
            intent=ctx.current_intent,
            target=ctx.current_resource,
            tool_responses=tool_responses,
            request_id=request_id,
            stream=stream
        )
        
        # 8. Save assistant response
        self.memory.add_message(request.conversation_id, "assistant", chat_response.answer)
        
        return chat_response
