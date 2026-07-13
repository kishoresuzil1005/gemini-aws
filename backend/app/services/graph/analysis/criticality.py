import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from app.services.graph.analysis.blast_radius import BlastRadiusAnalyzer

logger = logging.getLogger(__name__)

class CriticalityAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)
        self.blast_analyzer = BlastRadiusAnalyzer(self.neo4j)

    def analyze(self, resource_id: str):
        """
        Calculates a criticality score based on downstream reachability.
        A higher score indicates the resource acts as a critical dependency 
        for many downstream services.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream = self.dependency_analyzer.get_downstream(resource_id, depth=10)
        upstream = self.dependency_analyzer.get_upstream(resource_id, depth=10)
        blast_info = self.blast_analyzer.analyze(resource_id)
        
        downstream_count = len(downstream)
        upstream_count = len(upstream)
        blast_radius = blast_info.get("impacted_count", downstream_count)
        
        # Calculate a robust score
        resource_weight = 30 # default
        score = min(100, upstream_count * 2 + downstream_count * 5 + blast_radius * 2)
        
        if score > 80:
            level = "CRITICAL"
        elif score > 50:
            level = "HIGH"
        elif score > 20:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return {
            "resource": resource_id,
            "criticality_score": score,
            "criticality_level": level,
            "details": {
                "upstream": upstream_count,
                "downstream": downstream_count,
                "blast_radius": blast_radius,
                "resource_weight": resource_weight
            }
        }