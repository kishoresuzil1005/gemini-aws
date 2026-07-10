import pytest
from app.services.ai.assistant.planner import Planner
from app.services.ai.assistant.plan_executor import PlanExecutor
from app.services.ai.assistant.tool_router import ToolRouter
from app.services.ai.assistant.reasoning.reasoning_engine import ReasoningEngine
from app.services.ai.assistant.context.context_builder import ContextBuilder
from app.services.ai.assistant.response.response_generator import ResponseGenerator
from tests.mocks.fake_provider import FakeProvider
from app.services.ai.assistant.assistant_models import ConversationContext

def test_full_pipeline_sans_orchestrator():
    # 1. Planner
    planner = Planner()
    plan = planner.create_plan("c1", "SECURITY")
    
    # 2. Execution
    router = ToolRouter()
    executor = PlanExecutor(router)
    tool_results = executor.execute(plan)
    
    # 3. Reasoning
    reasoning = ReasoningEngine()
    reasoning_result = reasoning.process("c1", tool_results)
    
    # 4. Context
    ctx = ConversationContext(conversation_id="c1", current_intent="SECURITY", current_resource="r1")
    builder = ContextBuilder()
    context_str = builder.build_structured_context(ctx, reasoning_result)
    
    # 5. Response
    provider = FakeProvider(response_text="Mocked Pipeline Response")
    generator = ResponseGenerator(provider)
    chat_response = generator.generate("question", "history", context_str, "SECURITY", "r1", reasoning_result, "req_1")
    
    assert chat_response.answer == "Mocked Pipeline Response" or chat_response.answer != ""
    assert chat_response.status == "success"
