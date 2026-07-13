from typing import Dict, Any, Optional
from ..tool_registry import ToolRegistry, BaseTool

class ToolValidator:
    """
    Validates tool call payloads before execution — ensures required args are present
    and the tool is registered.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def validate(self, tool_name: str, args: Dict[str, Any]) -> tuple[bool, str]:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return False, f"Tool '{tool_name}' is not registered. Available: {self.registry.list_tools()}"

        # Each tool can declare required args via a `required_args` class attribute
        required = getattr(tool, "required_args", [])
        missing = [r for r in required if r not in args]
        if missing:
            return False, f"Tool '{tool_name}' missing required args: {missing}"

        return True, "