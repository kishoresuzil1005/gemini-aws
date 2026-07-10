import pytest
from app.services.ai.assistant.reasoning.reasoning_explainer import ReasoningExplainer
from app.services.ai.assistant.reasoning.reasoning_models import Finding, Evidence, Risk, Conflict

def test_explainer_content():
    explainer = ReasoningExplainer()
    finding = Finding(id="1", source_tool="T1", description="desc", raw_data={})
    evidence = Evidence(id="e1", finding_id="1", description="ev")
    risk = Risk(id="r1", finding_id="1", severity="CRITICAL", description="bad", score=100)
    conflict = Conflict(id="c1", description="bad", tools_involved=["T1"], resolved=True)
    
    exp = explainer.explain([finding], [evidence], [risk], [conflict])
    assert "Extracted 1 core findings" in exp
    assert "Resolved 1 conflicts" in exp
    assert "CRITICAL (100)" in exp
