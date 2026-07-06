import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class CriticalityAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)

    def analyze(self, resource_id: str):
        """
        Calculates a criticality score based on downstream reachability.
        A higher score indicates the resource acts as a critical dependency 
        for many downstream services.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        # A simple algorithm: base score of 10, plus 5 points for every downstream dependency.
        # This mirrors a localized Degree Centrality / Betweenness evaluation.
        downstream = self.dependency_analyzer.get_downstream(resource_id, depth=10)
        
        downstream_count = len(downstream)
        score = min(100, 10 + (downstream_count * 5))
        
        return {
            "resource": resource_id,
            "criticality_score": score,
            "downstream_count": downstream_count
        }
