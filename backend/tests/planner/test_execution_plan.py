import pytest
from app.services.ai.assistant.execution_plan import ExecutionPlan, ExecutionContext, PlanStatus, ExecutionStep, ToolRequirement

def test_execution_plan_creation():
    context = ExecutionContext(
        conversation_id="c1",
        request_id="r1",
        intent="SECURITY"
    )
    plan = ExecutionPlan(
        plan_id="p1",
        objective="Analyze security",
        context=context,
        status=PlanStatus.PENDING,
        required_tools=[ToolRequirement(tool_name="GraphTool")],
        steps=[ExecutionStep(step_number=1, tool_name="GraphTool", purpose="Test")],
        expected_outputs=["Graph"]
    )
    assert plan.plan_id == "p1"
    assert plan.status == PlanStatus.PENDING
    assert len(plan.steps) == 1
    assert plan.estimated_steps == 0 # default computed

def test_execution_plan_serialization():
    context = ExecutionContext(conversation_id="c1", request_id="r1", intent="SECURITY")
    plan = ExecutionPlan(
        plan_id="p1",
        objective="Analyze security",
        context=context,
        status=PlanStatus.PENDING
    )
    data = plan.model_dump()
    assert data["plan_id"] == "p1"
    assert data["status"] == "PENDING"
