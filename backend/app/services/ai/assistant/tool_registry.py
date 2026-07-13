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