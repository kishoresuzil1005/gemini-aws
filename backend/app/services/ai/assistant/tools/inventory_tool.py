import time
from app.services.ai.assistant.tool_registry import BaseTool
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.graph.neo4j_service import Neo4jService

class InventoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "INVENTORY"

    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        start_time = time.time()
        neo4j = Neo4jService()
        try:
            query = "MATCH (n) RETURN labels(n)[0] as type, count(n) as count"
            res = neo4j.query(query)
            context = [{"resource_type": r["type"], "count": r["count"]} for r in res]
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
        