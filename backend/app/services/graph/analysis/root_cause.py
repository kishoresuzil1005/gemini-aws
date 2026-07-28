import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from exceptions.analyzer_exceptions import KnowledgeNotFoundError

logger = logging.getLogger(__name__)

class RootCauseAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.dependency_analyzer = DependencyAnalyzer(self.client)

    def analyze(self, resource_id: str):
        """
        Traverses backwards (upstream) to find likely root causes 
        when a resource is unhealthy.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        upstream_nodes = self.dependency_analyzer.get_upstream(resource_id, depth=10)
        most_likely = upstream_nodes[0] if upstream_nodes else None
        confidence = 0.6 if most_likely else 0.0
        
        return {
            "symptom_resource": resource_id,
            "symptoms": [f"Analysis requested for {resource_id}"],
            "evidence": upstream_nodes,
            "possible_root_causes": upstream_nodes,
            "most_likely_cause": most_likely,
            "confidence": confidence,
            "recommended_actions": (
                ["Inspect the upstream dependency configuration and health status."]
                if most_likely else []
            ),
        }
