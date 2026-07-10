from typing import List
from app.services.ai.assistant.execution_plan import ToolResult, ToolStatus

class RootCauseAnalyzer:
    """
    Analyzes cross-tool evidence to pinpoint definitive root causes.
    """
    def analyze(self, tool_results: List[ToolResult]) -> List[ToolResult]:
        for tr in tool_results:
            if "reasoning" not in tr.metadata:
                tr.metadata["reasoning"] = {}
                
            tr.metadata["reasoning"]["is_root_cause"] = False
            
            # Simple heuristic for Phase 4
            if tr.tool_name == "RootCauseTool" and tr.status == ToolStatus.SUCCESS:
                tr.metadata["reasoning"]["is_root_cause"] = True
                
        return tool_results
