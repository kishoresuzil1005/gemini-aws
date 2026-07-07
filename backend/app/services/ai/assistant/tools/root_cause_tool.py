import time
from app.services.ai.assistant.tool_registry import BaseTool
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.graph.analysis.root_cause import RootCauseAnalyzer

class RootCauseTool(BaseTool):
    @property
    def name(self) -> str:
        return "ROOT_CAUSE"

    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        start_time = time.time()
        analyzer = RootCauseAnalyzer()
        try:
            result = analyzer.analyze(resource_id)
            status = "SUCCESS"
        except Exception as e:
            result = {"error": str(e)}
            status = "ERROR"
            
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return ToolResponse(
            tool_name=self.name,
            status=status,
            execution_time_ms=execution_time_ms,
            context=result
        )
