import logging
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class RootCauseAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)

    def analyze(self, resource_id: str):
        """
        Traverses backwards (upstream) to find likely root causes 
        when a resource is unhealthy.
        """
        upstream_nodes = self.dependency_analyzer.get_upstream(resource_id, depth=10)
        
        return {
            "symptom_resource": resource_id,
            "possible_root_causes": upstream_nodes
        }
