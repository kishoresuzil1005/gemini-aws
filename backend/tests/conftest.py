import pytest
from app.services.ai.assistant.reasoning.reasoning_engine import ReasoningEngine

@pytest.fixture
def reasoning():
    return ReasoningEngine()
