"""The single production pipeline used by GraphAssistant chat requests."""

import asyncio
import uuid
from typing import Optional

from app.services.ai.assistant.assistant_models import ChatRequest, ChatResponse, ExecutionContext
from app.services.ai.assistant.conversation.conversation_manager import ConversationManager
from app.services.ai.assistant.intent_classifier import IntentClassifier
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.prompt_builder import PromptBuilder
from app.services.ai.assistant.query_resolver import QueryResolver
from app.services.ai.assistant.reasoning.reasoning_engine import ReasoningEngine
from app.services.ai.assistant.response.response_generator import ResponseGenerator
from app.services.ai.context_engine import ContextEngine, ContextLevel, ContextRequest
from app.services.ai.context_engine.models import AIContext


class AssistantPipeline:
    """Conversation -> resolve -> context -> analysis -> reasoning -> response."""

    def __init__(
        self,
        *,
        conversation: ConversationManager,
        provider: BaseProvider,
        classifier: Optional[IntentClassifier] = None,
        resolver: Optional[QueryResolver] = None,
        context_engine: Optional[ContextEngine] = None,
        reasoning_engine: Optional[ReasoningEngine] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        response_generator: Optional[ResponseGenerator] = None,
    ) -> None:
        self.conversation = conversation
        self.memory = conversation.memory
        self.classifier = classifier or IntentClassifier()
        self.resolver = resolver or QueryResolver()
        self.context_engine = context_engine or ContextEngine()
        self.reasoning_engine = reasoning_engine or ReasoningEngine()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.generator = response_generator or ResponseGenerator(provider)

    def process(self, request: ChatRequest, stream: bool = False) -> ChatResponse:
        request_id = str(uuid.uuid4())
        intent_data = self.classifier.classify(request.message)
        previous_context = self.memory.get_context(request.conversation_id)
        execution_context = ExecutionContext(
            user_message=request.message,
            intent=intent_data["intent"],
            identifier=previous_context.current_resource,
            session_id=request.conversation_id,
        )
        query = self.resolver.resolve(execution_context)
        execution_context = execution_context.model_copy(update={"identifier": query.identifier})

        intent_data["target_resource"] = query.identifier
        conversation_context = self.conversation.process_turn(request.conversation_id, intent_data)
        self.memory.add_message(request.conversation_id, "user", request.message)

        ai_context = self._build_context(execution_context)
        reasoning = self.reasoning_engine.process(request.conversation_id, ai_context)
        history = self.conversation.get_formatted_history(request.conversation_id, limit=5)
        messages, context_text = self.prompt_builder.build(
            question=request.message,
            history=history,
            context=ai_context,
            reasoning=reasoning,
            intent=conversation_context.current_intent or "UNKNOWN",
        )
        response = self.generator.generate_messages(
            messages=messages,
            context_str=context_text,
            intent=conversation_context.current_intent or "UNKNOWN",
            target=conversation_context.current_resource,
            reasoning_result=reasoning,
            request_id=request_id,
            stream=stream,
        )
        self.memory.add_message(request.conversation_id, "assistant", response.answer or "")
        return response

    def _build_context(self, execution_context: ExecutionContext) -> AIContext:
        if not execution_context.identifier:
            return AIContext()
        request = ContextRequest(
            identifier=execution_context.identifier,
            level=execution_context.analysis_depth,
            include_metrics=execution_context.include_metrics,
            include_cost=execution_context.include_cost,
        )
        try:
            return asyncio.run(self.context_engine.build(request))
        except Exception:
            # The LLM can still answer a general question when data providers are
            # unavailable.  Provider execution details remain observable in logs.
            return AIContext()
