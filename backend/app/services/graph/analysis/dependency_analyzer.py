import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()

    def get_dependencies(self, resource_id: str, depth: int = 5):
        """
        Fetches upstream and downstream dependencies for a given resource
        up to the specified depth.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream = self.get_downstream(resource_id, depth)
        upstream = self.get_upstream(resource_id, depth)
        
        return {
            "resource": resource_id,
            "upstream": upstream,
            "downstream": downstream,
            "depth": depth
        }

    def get_downstream(self, resource_id: str, depth: int = 5):
        if not self.neo4j.driver:
            return []
            
        try:
            query = f"""
            MATCH path=(n {{id:$resource_id}})-[*1..{depth}]->(m)
            RETURN DISTINCT
                m.id as id,
                labels(m) as labels
            """
            res = self.neo4j.query(query, resource_id=resource_id)
            if res:
                for r in res:
                    if not isinstance(r.get("labels"), list):
                        r["labels"] = [r.get("labels") or "Resource"]
                return res
            return []
        except Exception as e:
            logger.error(f"Error querying downstream dependencies: {e}")
            return []

    def get_upstream(self, resource_id: str, depth: int = 5):
        if not self.neo4j.driver:
            return []
            
        try:
            query = f"""
            MATCH path=(a)-[*1..{depth}]->(b {{id:$resource_id}})
            RETURN DISTINCT
                a.id as id,
                labels(a) as labels
            """
            res = self.neo4j.query(query, resource_id=resource_id)
            if res:
                for r in res:
                    if not isinstance(r.get("labels"), list):
                        r["labels"] = [r.get("labels") or "Resource"]
                return res
            return []
        except Exception as e:
            logger.error(f"Error querying upstream dependencies: {e}")
            return []
