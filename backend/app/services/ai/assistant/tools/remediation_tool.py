import time
from app.services.ai.assistant.tool_registry import BaseTool
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.ai.remediation_planner import RemediationPlanner

class RemediationTool(BaseTool):
    @property
    def name(self) -> str:
        return "REMEDIATION"

    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        start_time = time.time()
        planner = RemediationPlanner()
        try:
            results = planner.plan_for_resource(resource_id)
            context = [p.dict() for p in results]
            status = "SUCCESS"
        except Exception as e:
            context = {"error": str(e)}
            status = "ERROR"
            
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return ToolResponse(
            tool_name=self.name,
            status=status,
            execution_time_ms=execution_time_ms,
            context=context
        )