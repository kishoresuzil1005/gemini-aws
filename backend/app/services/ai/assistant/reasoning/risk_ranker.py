from typing import List
from app.services.ai.assistant.execution_plan import ToolResult, ToolStatus

class RiskRanker:
    """
    Evaluates the outputs from security and dependency tools to dynamically rank issues.
    """
    def rank(self, tool_results: List[ToolResult]) -> List[ToolResult]:
        for tr in tool_results:
            if "reasoning" not in tr.metadata:
                tr.metadata["reasoning"] = {}
                
            # Naive ranking for Phase 4
            risk_score = 0
            if tr.tool_name == "SecurityTool" and tr.status == ToolStatus.SUCCESS:
                risk_score = 80 # default high severity flag
                
            tr.metadata["reasoning"]["risk_score"] = risk_score
            
        return tool_result