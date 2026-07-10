import pytest
from app.services.ai.assistant.execution_plan import ToolStatus
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.ai.assistant.tool_registry import BaseTool

class DummyGraphTool(BaseTool):
    @property
    def name(self) -> str:
        return "GraphTool"
        
    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        return ToolResponse(tool_name="GraphTool", status="success", context={"data": "graph"})

class DummyFailTool(BaseTool):
    @property
    def name(self) -> str:
        return "FailTool"
        
    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        return ToolResponse(tool_name="FailTool", status="error", context={})

def test_plan_executor_success(executor, planner):
    executor.router.registry.register(DummyGraphTool())
    
    plan = planner.create_plan("c1", "INVENTORY") # Needs InventoryTool, GraphTool
    # Let's manually set tools to just GraphTool for testing
    plan.steps = [plan.steps[0]] # Just one step
    plan.steps[0].tool_name = "GraphTool"
    plan.required_tools = [plan.required_tools[0]]
    plan.required_tools[0].tool_name = "GraphTool"
    
    results = executor.execute(plan)
    assert len(results) == 1
    assert results[0].tool_name == "GraphTool"
    assert results[0].status == ToolStatus.SUCCESS

def test_plan_executor_missing_tool(executor, planner):
    plan = planner.create_plan("c1", "SECURITY")
    results = executor.execute(plan)
    # Since tools aren't registered, they should all fail/skip
    for result in results:
        assert result.status in [ToolStatus.FAILED, ToolStatus.SKIPPED]

def test_plan_executor_dependency_skip(executor, planner):
    executor.router.registry.register(DummyFailTool())
    plan = planner.create_plan("c1", "SECURITY")
    # Change first step to FailTool
    plan.steps[0].tool_name = "FailTool"
    plan.steps[1].depends_on = ["FailTool"]
    
    results = executor.execute(plan)
    
    fail_result = next(r for r in results if r.tool_name == "FailTool")
    assert fail_result.status == ToolStatus.FAILED
    
    # Because FailTool failed, the next step that depends on it should be skipped
    skip_result = next(r for r in results if r.tool_name == plan.steps[1].tool_name)
    assert skip_result.status == ToolStatus.SKIPPED
