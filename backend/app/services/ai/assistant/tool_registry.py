from typing import Dict, Any, Type
from abc import ABC, abstractmethod
from app.services.ai.assistant.assistant_models import ToolResponse

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def execute_tool(self, name: str, resource_id: str, **kwargs) -> ToolResponse:
        tool = self.get_tool(name)
        if not tool:
            return None
            
        try:
            return tool.execute(resource_id=resource_id, **kwargs)
        except Exception as e:
            print(f"TOOL ERROR [{name}]: {e}")
            return ToolResponse(
                tool_name=name,
                status="error",
                execution_time_ms=0,
                context={"error": f"Tool execution failed: {str(e)}"},
                metadata={"error_type": type(e).__name__}
            )
