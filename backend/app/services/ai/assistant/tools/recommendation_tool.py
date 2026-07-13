import time
from app.services.ai.assistant.tool_registry import BaseTool
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.ai.recommendation_engine import AIRecommendationEngine

class RecommendationTool(BaseTool):
    @property
    def name(self) -> str:
        return "RECOMMENDATION"

    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        start_time = time.time()
        engine = AIRecommendationEngine()
        try:
            results = engine.analyze_resource(resource_id)
            context = [r.dict() for r in results]
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
        