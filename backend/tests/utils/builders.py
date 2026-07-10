from typing import Dict, Any, List
from app.services.ai.assistant.execution_plan import ToolResult, ToolStatus

def build_tool_result(tool_name: str, status: ToolStatus = ToolStatus.SUCCESS, context: Any = None, metadata: Dict[str, Any] = None) -> ToolResult:
    return ToolResult(
        tool_name=tool_name,
        status=status,
        context=context or {},
        metadata=metadata or {},
        started_at="2024-01-01T00:00:00Z",
        finished_at="2024-01-01T00:00:01Z",
        execution_time_ms=1000
    )
