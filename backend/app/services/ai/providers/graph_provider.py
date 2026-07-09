from typing import Dict, Any

class GraphProvider:
    def get_context(self, resource_id: str) -> Dict[str, Any]:
        return {"source": "Neo4j", "data": "graph context for " + str(resource_id)}
