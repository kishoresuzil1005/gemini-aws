import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from exceptions.analyzer_exceptions import KnowledgeNotFoundError

logger = logging.getLogger(__name__)

class BlastRadiusAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.dependency_analyzer = DependencyAnalyzer(self.client)

    def analyze(self, resource_id: str):
        """
        Determines the impact of a resource failure by finding all downstream
        services that depend on it directly or indirectly.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream_nodes = self.dependency_analyzer.get_downstream(resource_id, depth=10)
        
        return {
            "resource": resource_id,
            "impacted_count": len(downstream_nodes),
            "impacted_resources": downstream_nodes
        }