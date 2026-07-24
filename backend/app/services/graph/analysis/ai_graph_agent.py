import logging
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.architecture_review import ArchitectureReviewer

logger = logging.getLogger(__name__)

class AIGraphAgent:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.architecture_reviewer = ArchitectureReviewer(self.client)

    def generate_recommendations(self):
        """
        Gathers graph data (architecture warnings, isolated nodes, etc.)
        and feeds it to an LLM to generate plain-text recommendations.
        """
        # Step 1: Gather Context
        arch_data = self.architecture_reviewer.analyze()
        
        # MOCK LLM RESPONSE
        recommendations = [
            "Unused Security Groups detected: Consider cleaning up orphaned SGs to reduce attack surface.",
            "Unused EBS Volumes: Several volumes have no ATTACHED_TO relationships. Deleting them will save costs.",
            "Single Point of Failure: Some EC2 instances are not part of an Auto Scaling Group.",
            "Missing Backup: RDS instances are missing cross-region snapshot replication.",
            "High Blast Radius: The primary VPC Route Table routes traffic for 14 downstream subnets."
        ]
        
        return {
            "status": "success",
            "context_analyzed": arch_data,
            "recommendations": recommendations
        }