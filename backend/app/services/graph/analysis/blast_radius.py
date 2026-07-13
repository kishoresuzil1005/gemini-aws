import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class BlastRadiusAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)

    def analyze(self, resource_id: str):
        """
        Determines the impact of a resource failure by finding all downstream
        services that depend on it directly or indirectly.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream_nodes = self.dependency_analyzer.get_downstream(resource_id, depth=10)
        
        return {
            "resource": resource_id,
            "impacted_count": len(downstream_nodes),
            "impacted_resources": downstream_nodes
        