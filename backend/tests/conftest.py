import pytest
from app.services.ai.assistant.planner import Planner
from app.services.ai.assistant.plan_executor import PlanExecutor
from app.services.ai.assistant.tool_router import ToolRouter
from app.services.ai.assistant.reasoning.reasoning_engine import ReasoningEngine

@pytest.fixture
def planner():
    return Planner()

@pytest.fixture
def tool_router():
    return ToolRouter()

@pytest.fixture
def executor(tool_router):
    return PlanExecutor(tool_router)

@pytest.fixture
def reasoning():
    return ReasoningEngine()
