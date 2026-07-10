import pytest
from app.services.ai.assistant.tool_router import ToolRouter
from app.services.ai.assistant.tool_registry import BaseTool
from app.services.ai.assistant.assistant_models import ToolResponse

class MockTool(BaseTool):
    @property
    def name(self) -> str:
        return "MockTool"
        
    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        return ToolResponse(tool_name="MockTool", status="success")

def test_tool_router_get_registered():
    router = ToolRouter()
    tool = MockTool()
    router.registry.register(tool)
    
    fetched = router.get_tool("MockTool")
    assert fetched is not None
    assert fetched.name == "MockTool"

def test_tool_router_missing_tool():
    router = ToolRouter()
    assert router.get_tool("NonExistentTool") is None
