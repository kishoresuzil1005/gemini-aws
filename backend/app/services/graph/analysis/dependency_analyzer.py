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
        """Resources that depend ON the given resource (or are connected downstream)."""
        if not self.neo4j.driver:
            return []
            
        try:
            # Use undirected (-) to capture both directed and undirected relationships
            # This ensures IN_VPC, IN_SUBNET, USES_SG etc. are all returned
            query = f"""
            MATCH path=(n {{id:$resource_id}})-[*1..{depth}]-(m)
            WHERE m.id <> $resource_id
            RETURN DISTINCT
                m.id as id,
                m.name as name,
                labels(m) as labels,
                [rel in relationships(path) | type(rel)][0] as relation_type
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
        """Resources that the given resource depends ON."""
        if not self.neo4j.driver:
            return []
            
        try:
            # For upstream: look for resources that have outgoing directed edges TO this resource
            # Fall back to undirected if nothing found via directed
            query = f"""
            MATCH path=(a)-[*1..{depth}]->(b {{id:$resource_id}})
            WHERE a.id <> $resource_id
            RETURN DISTINCT
                a.id as id,
                a.name as name,
                labels(a) as labels,
                [rel in relationships(path) | type(rel)][0] as relation_type
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