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
        
        return {
            "symptom_resource": resource_id,
            "possible_root_causes": upstream_nodes
        }