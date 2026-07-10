from app.providers.kubernetes.auth import KubernetesAuth
from app.providers.kubernetes.models import KubernetesResourceMetadata

class ClusterDiscovery:
    def __init__(self, auth: KubernetesAuth):
        self.auth = auth
        self.api = auth.core_v1

    def get_cluster_info(self) -> KubernetesResourceMetadata:
        # A simple mock to get "cluster" representing the current context
        return KubernetesResourceMetadata(
            id="cluster",
            name="kubernetes-cluster",
            type="Cluster"
        )
