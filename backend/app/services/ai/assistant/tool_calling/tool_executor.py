from typing import Dict, Any, Optional
from ..tool_registry import ToolRegistry
from .tool_parser import ToolCallParser
from .tool_validator import ToolValidator

class ToolExecutor:
    """
    Orchestrates the full tool calling loop:
      LLM Response → Parse → Validate → Execute → Return result to LLM.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.parser = ToolCallParser()
        self.validator = ToolValidator(registry)

    def process_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Checks if the LLM wants to call a tool. If so, executes it and returns the result.
        """
        tool_call, clean_text = self.parser.extract(llm_response)

        if not tool_call:
            return {"used_tool": False, "text": llm_response}

        tool_name = tool_call.get("tool")
        args = tool_call.get("args", {})

        is_valid, error_msg = self.validator.validate(tool_name, args)
        if not is_valid:
            print(f"[ToolExecutor] Validation failed: {error_msg}")
            return {"used_tool": False, "text": clean_text, "tool_error": error_msg}

        tool = self.registry.get_tool(tool_name)
        try:
            result = tool.execute(**args)
            print(f"[ToolExecutor] Tool '{tool_name}' executed successfully.")
            return {
                "used_tool": True,
                "tool_name": tool_name,
                "tool_result": result,
                "text": clean_text
            }
        except Exception as e:
            print(f"[ToolExecutor] Tool '{tool_name}' raised an error: {e}")
            return {"used_tool": False, "text": clean_text, "tool_error": str(e)