import logging
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class SecurityImpactAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)

    def analyze(self, resource_id: str):
        """
        Calculates the security exposure of a resource (e.g., a SecurityGroup).
        By traversing backwards (upstream), we can see what resources 
        are exposed if this specific resource is compromised.
        """
        # A Security Group sits in front of resources, so the resources
        # depend on the SG. This means the resources are upstream of the SG 
        # in our graph schema (e.g. EC2 -[USES_SG]-> SecurityGroup).
        # We traverse upstream to see all resources reachable.
        exposed_resources = self.dependency_analyzer.get_upstream(resource_id, depth=10)
        
        return {
            "compromised_resource": resource_id,
            "exposure_count": len(exposed_resources),
            "exposed_resources": exposed_resources
        }
