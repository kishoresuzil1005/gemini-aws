import pytest
from app.services.ai.assistant.execution_plan import PlanStatus

def test_planner_security_intent(planner):
    plan = planner.create_plan("c1", "SECURITY")
    assert plan.status == PlanStatus.PENDING
    assert plan.objective != ""
    tools = [t.tool_name for t in plan.required_tools]
    assert "SecurityTool" in tools
    assert "GraphTool" in tools
    assert plan.steps[0].tool_name == "GraphTool" # Graph runs first

def test_planner_inventory_intent(planner):
    plan = planner.create_plan("c1", "INVENTORY")
    tools = [t.tool_name for t in plan.required_tools]
    assert "InventoryTool" in tools
    
def test_planner_invalid_dependencies(planner):
    # This checks internal validation
    plan = planner.create_plan("c1", "SECURITY")
    assert plan.status != PlanStatus.FAILED # Should pass normally
    
    # Manually break it to test validation logic
    plan.steps[0].depends_on = ["MissingTool"]
    planner._validate_plan(plan)
    assert plan.status == PlanStatus.FAILED
    assert "Invalid dependency" in plan.context.metadata["error"]

def test_planner_duplicate_tools(planner):
    plan = planner.create_plan("c1", "SECURITY")
    plan.required_tools.append(plan.required_tools[0])
    planner._validate_plan(plan)
    assert plan.status == PlanStatus.FAILED
    assert "Duplicate tools" in plan.context.metadata["error"]
