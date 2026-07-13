from typing import List
from app.services.ai.assistant.knowledge_graph.builders.graph_builder import BaseGraphBuilder
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge

class KubernetesGraphBuilder(BaseGraphBuilder):
    """Mocks fetching K8s topology."""
    
    def __init__(self, discovery_client=None):
        self.client = discovery_client
        
    def build_nodes(self) -> List[CloudNode]:
        nodes = []
        resources = [
            {"uri": "namespaces/default/deployments/payment-service"},
            {"uri": "namespaces/default/pods/payment-service-pod-1", "owner_ref": "payment-service"}
        ]
        
        from app.providers.common.resource_identifier import GenericResourceIdentifier
        
        for res in resources:
            identifier = GenericResourceIdentifier.parse_kubernetes_uri(res["uri"])
            nodes.append(CloudNode(
                node_id=identifier.unique_id,
                provider="KUBERNETES",
                resource_type=identifier.resource_type,
                resource_name=identifier.resource_name,
                properties=res
            ))
        return nodes
        
    def build_edges(self) -> List[CloudEdge]:
        # K8s explicitly manages parent-child (OwnerReferences)
        return [