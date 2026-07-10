import re
import json
from typing import Dict, Any, Optional, Tuple

class ToolCallParser:
    """
    Parses Ollama responses for structured tool call instructions.
    Supports both JSON block format and natural language patterns.
    
    Expected LLM output format:
        ```tool_call
        {"tool": "security_tool", "args": {"resource_id": "i-12345"}}
        ```
    """
    TOOL_CALL_PATTERN = re.compile(r"```tool_call\s*(.*?)\s*```", re.DOTALL)

    def extract(self, llm_response: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Returns (tool_call_dict | None, cleaned_text_without_tool_block)
        """
        match = self.TOOL_CALL_PATTERN.search(llm_response)
        if not match:
            return None, llm_response

        raw_json = match.group(1).strip()
        clean_text = self.TOOL_CALL_PATTERN.sub("", llm_response).strip()

        try:
            tool_call = json.loads(raw_json)
            return tool_call, clean_text
        except json.JSONDecodeError as e:
            print(f"[ToolCallParser] Failed to parse tool call JSON: {e}")
            return None, llm_response
