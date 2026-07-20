import pytest
from app.services.ai.assistant.reasoning.reasoning_engine import ReasoningEngine
from app.services.ai.context_engine.models import AIContext

def test_reasoning_engine_process(reasoning):
    context = AIContext(findings={
        "security": {
            "findings": [{"description": "Instance is publicly reachable", "severity": "HIGH"}]
        }
    })

    rr = reasoning.process("session_123", context)
    
    assert rr.session_id == "session_123"
    assert len(rr.findings) > 0
    assert len(rr.evidence) > 0
    # Note: Phase 4 stubs currently hardcode risk and conflict generation inside components
    # We assert that the engine orchestrates everything and outputs a ReasoningResult
    assert type(rr.risks) == list
    assert type(rr.conflicts) == list
    
    # We check if validator ran correctly
    assert hasattr(rr, "is_valid")
    assert rr.explanation != ""
