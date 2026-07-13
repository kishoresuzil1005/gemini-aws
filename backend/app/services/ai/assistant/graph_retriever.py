from typing import Dict, Any
from app.services.graph.neo4j_service import Neo4jService

class GraphRetriever:
    def __init__(self):
        self.neo4j = Neo4jService()

    def get_resource_context(self, resource_id: str) -> Dict[str, Any]:
        """
        Retrieves direct immediate context about a resource from the graph.
        """
        context = {}
        if not self.neo4j.driver:
            return context
            
        try:
            # Get resource properties
            res = self.neo4j.query("MATCH (n {id: $id}) RETURN properties(n) as props, labels(n) as labels", id=resource_id)
            if res:
                context["properties"] = res[0].get("props", {})
                context["type"] = res[0].get("labels", [])
                
            # Get immediate neighbors
            neighbors = self.neo4j.query(
                "MATCH (n {id: $id})-[r]-(m) RETURN type(r) as rel, m.id as id, labels(m)[0] as type",
                id=resource_id
            )
            context["neighbors"] = [
                {"relationship": r["rel"], "target_id": r["id"], "target_type": r["type"]}
                for r in neighbors
            ]
        except Exception:
            pass
            
        return contex