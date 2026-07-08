from typing import Dict, Any, List
from app.services.ai.assistant.memory.memory_manager import MemoryManager
from app.services.ai.assistant.memory.memory_store import MemoryStore
from app.services.ai.assistant.memory.session_manager import SessionManager
from app.services.ai.assistant.history.history_manager import HistoryManager
from app.services.ai.assistant.conversation.conversation_manager import ConversationManager
from app.services.ai.assistant.intent_classifier import IntentClassifier
from app.services.ai.assistant.tool_router import ToolRouter
from app.services.ai.assistant.context.context_builder import ContextBuilder
from app.services.ai.assistant.response.response_generator import ResponseGenerator
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.llm.ollama_provider import OllamaProvider
from app.services.ai.assistant.llm.config import settings
from app.services.ai.assistant.resource_validator import ResourceValidator
from app.services.ai.assistant.resource_extractor import ResourceExtractor
import uuid
from app.services.ai.assistant.assistant_models import ChatResponse, ChatRequest

class GraphAssistant:
    def __init__(self, memory_manager: MemoryManager = None, provider: BaseProvider = None):
        if not memory_manager:
            memory_store = MemoryStore()
            memory_manager = MemoryManager(memory_store)
        self.memory = memory_manager
        
        self.session_manager = SessionManager()
        self.history_manager = HistoryManager(self.memory.store)
        self.conversation = ConversationManager(self.memory, self.session_manager, self.history_manager)
        
        self.classifier = IntentClassifier()
        self.extractor = ResourceExtractor()
        self.tool_router = ToolRouter()
        self.context_builder = ContextBuilder()
        self.provider = provider or OllamaProvider(settings)
        self.generator = ResponseGenerator(self.provider)
        self.validator = ResourceValidator()

    def chat(self, request: ChatRequest, stream: bool = False) -> ChatResponse:
        request_id = str(uuid.uuid4())
        print(f"[Req: {request_id}] Starting AI Chat for Conversation: {request.conversation_id}")
        
        # 1. Intent Classification & Candidate Extraction
        intent_data = self.classifier.classify(request.message)
        candidate = self.extractor.extract(request.message)
        
        # 2. Resource Resolution
        resolved = self.validator.resolve(candidate, request.conversation_id)
        
        # 3. Short-circuit on missing resources
        if candidate and resolved.confidence < 1.0 and intent_data.get("intent") not in ["DOCUMENTATION", "UNKNOWN"]:
            return ChatResponse(
                status="error",
                data=None,
                errors=[
                    {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Resource '{candidate}' was not found.",
                        "resource": candidate,
                        "did_you_mean": resolved.suggestions,
                    }
                ],
            )
            
        # 4. Bind validated context
        intent_data["target_resource"] = resolved.resource_id
        
        # 5. Conversation Context Processing
        ctx = self.conversation.process_turn(request.conversation_id, intent_data)
        ctx.current_resource_type = resolved.resource_type
        ctx.current_resource_confidence = resolved.confidence
        
        # 6. Add to Memory (Only if Valid!)
        self.memory.add_message(request.conversation_id, "user", request.message)
        
        # 5. Tool Execution
        tool_responses = []
        if ctx.current_intent != "UNKNOWN":
            trs = self.tool_router.route(ctx.current_intent, ctx.current_resource)
            tool_responses.extend(trs)
            
        # 5. Context Building
        context_str = self.context_builder.build_structured_context(ctx, tool_responses)
        
        # 6. History formatting
        history_str = self.conversation.get_formatted_history(request.conversation_id, limit=5)
        
        # Memory summary integration (Phase 4)
        memory_summary = self.memory.summarize_memory(request.conversation_id)
        context_str = self.context_builder.build_structured_context(ctx, tool_responses, memory_context=memory_summary)
        
        # 7. Structured Logging (Phase 9/10)
        import time
        import logging
        logger = logging.getLogger("GraphAssistant")
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            logger.addHandler(ch)
            logger.setLevel(logging.INFO)
            
        used_tools = [tr.tool_name for tr in tool_responses]
        prompt_len = len(request.message)
        context_len = len(context_str)
        
        logger.info(f"Intent: {ctx.current_intent}")
        logger.info(f"Resource: {ctx.current_resource}")
        logger.info(f"Tool: {', '.join(used_tools) if used_tools else 'None'}")
        logger.info(f"Prompt: {prompt_len} chars")
        logger.info(f"Context: {context_len} chars")
        logger.info(f"Model: {settings.ollama_model}")
        
        gen_start_time = time.time()
        
        # 8. Response Generation
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
        
        gen_elapsed = time.time() - gen_start_time
        logger.info(f"Time: {gen_elapsed:.2f} sec")
        
        # 9. Save assistant response
        self.memory.add_message(request.conversation_id, "assistant", chat_response.answer)
        
        return chat_response
