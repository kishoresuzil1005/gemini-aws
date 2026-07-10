import pytest
from app.services.ai.assistant.reasoning.conflict_resolver import ConflictResolver
from app.services.ai.assistant.reasoning.reasoning_models import Finding

def test_conflict_resolver_resolution():
    resolver = ConflictResolver()
    findings = [
        Finding(id="1", source_tool="SecurityTool", description="Public RDS", raw_data={}),
        Finding(id="2", source_tool="InventoryTool", description="Private RDS", raw_data={})
    ]
    
    conflicts = resolver.resolve_conflicts(findings)
    assert len(conflicts) == 1
    assert conflicts[0].resolved is True
    # In reasoning_rules, InventoryTool (90) > SecurityTool (80)
    assert conflicts[0].winner == "InventoryTool"

def test_conflict_resolver_no_conflict():
    resolver = ConflictResolver()
    findings = [
        Finding(id="1", source_tool="SecurityTool", description="Public RDS", raw_data={})
    ]
    conflicts = resolver.resolve_conflicts(findings)
    assert len(conflicts) == 0
