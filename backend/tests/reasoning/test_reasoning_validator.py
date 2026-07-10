import pytest
from app.services.ai.assistant.reasoning.reasoning_validator import ReasoningValidator
from app.services.ai.assistant.reasoning.reasoning_models import Finding, Evidence, Risk, Conflict

def test_validator_missing_evidence():
    validator = ReasoningValidator()
    finding = Finding(id="1", source_tool="T1", description="desc", raw_data={})
    is_valid, errors = validator.validate([finding], [], [], [])
    assert is_valid is False
    assert "No supporting evidence found." in errors

def test_validator_broken_reference():
    validator = ReasoningValidator()
    finding = Finding(id="1", source_tool="T1", description="desc", raw_data={})
    evidence = Evidence(id="e1", finding_id="MISSING_ID", description="ev")
    is_valid, errors = validator.validate([finding], [evidence], [], [])
    assert is_valid is False
    assert any("Broken reference" in e for e in errors)

def test_validator_unresolved_conflict():
    validator = ReasoningValidator()
    finding = Finding(id="1", source_tool="T1", description="desc", raw_data={})
    evidence = Evidence(id="e1", finding_id="1", description="ev")
    conflict = Conflict(id="c1", description="bad", tools_involved=["T1"], resolved=False)
    
    is_valid, errors = validator.validate([finding], [evidence], [], [conflict])
    assert is_valid is False
    assert any("Unresolved conflict detected" in e for e in errors)
