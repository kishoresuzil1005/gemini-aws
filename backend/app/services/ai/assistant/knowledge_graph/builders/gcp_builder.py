from typing import List
from app.services.ai.assistant.knowledge_graph.builders.graph_builder import BaseGraphBuilder
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge
from app.providers.common.resource_identifier import GenericResourceIdentifier

class GCPGraphBuilder(BaseGraphBuilder):
    """Parses GCP Cloud Asset Inventory / Discovery responses into CloudNodes."""
    
    def __init__(self, discovery_client=None):
        self.client = discovery_client
        
    def build_nodes(self) -> List[CloudNode]:
        nodes = []
        # Simulate fetching resources: e.g. Compute Instances, VPCs
        resources = [
            {"name": "projects/my-proj/zones/us-central1-a/instances/vm1", "type": "compute.googleapis.com/Instance"}
        ]
        
        for res in resources:
            identifier = GenericResourceIdentifier.parse_gcp_uri(res["name"])
            nodes.append(CloudNode(
                node_id=identifier.unique_id,
                provider="GCP",
                resource_type=identifier.resource_type,
                resource_name=identifier.resource_name,
                properties=res
            ))
        return nodes
        
    def build_edges(self) -> List[CloudEdge]:
        # GCP specific edge building
        return []