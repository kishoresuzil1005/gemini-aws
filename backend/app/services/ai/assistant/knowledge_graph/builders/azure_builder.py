from typing import List, Dict, Any
from app.services.ai.assistant.knowledge_graph.builders.graph_builder import BaseGraphBuilder
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge
from app.providers.common.resource_identifier import GenericResourceIdentifier

class AzureGraphBuilder(BaseGraphBuilder):
    """Parses Azure Resource Graph / Discovery responses into CloudNodes."""
    
    def __init__(self, discovery_client=None):
        self.client = discovery_client
        
    def build_nodes(self) -> List[CloudNode]:
        nodes = []
        # Simulate fetching resources: e.g. Virtual Machines, VNets
        # In real implementation: resources = self.client.get_all_resources()
        resources = [
            {"id": "/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1", "type": "Microsoft.Compute/virtualMachines", "name": "vm-1"}
        ]
        
        for res in resources:
            identifier = GenericResourceIdentifier.parse_azure_id(res["id"])
            nodes.append(CloudNode(
                node_id=identifier.unique_id,
                provider="AZURE",
                resource_type=identifier.resource_type,
                resource_name=identifier.resource_name,
                properties=res
            ))
        return nodes
        
    def build_edges(self) -> List[CloudEdge]:
        # Azure specific edge building (e.g. NIC -> Subnet)
        return []
