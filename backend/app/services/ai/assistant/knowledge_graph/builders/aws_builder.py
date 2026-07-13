from typing import List
from app.services.ai.assistant.knowledge_graph.builders.graph_builder import BaseGraphBuilder
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge
from app.providers.common.resource_identifier import GenericResourceIdentifier

class AWSGraphBuilder(BaseGraphBuilder):
    """Mocks fetching AWS topology."""
    
    def __init__(self, discovery_client=None):
        self.client = discovery_client
        
    def build_nodes(self) -> List[CloudNode]:
        nodes = []
        resources = [
            {"arn": "arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890", "subnet_id": "subnet-123"}
        ]
        
        for res in resources:
            identifier = GenericResourceIdentifier.parse_aws_arn(res["arn"])
            nodes.append(CloudNode(
                node_id=identifier.unique_id,
                provider="AWS",
                resource_type=identifier.resource_type,
                resource_name=identifier.resource_name,
                properties=res
            ))
        return nodes
        
    def build_edges(self) -> List[CloudEdge]:
        # Leave explicit edges empty if RelationshipEngine will handle it, or add explicit ones here
        return []