import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from app.services.graph.analysis.blast_radius import BlastRadiusAnalyzer
from exceptions.analyzer_exceptions import KnowledgeNotFoundError

logger = logging.getLogger(__name__)

class CriticalityAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.dependency_analyzer = DependencyAnalyzer(self.client)
        self.blast_analyzer = BlastRadiusAnalyzer(self.client)

    def analyze(self, resource_id: str):
        """
        Calculates a criticality score based on downstream reachability.
        A higher score indicates the resource acts as a critical dependency 
        for many downstream services.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
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