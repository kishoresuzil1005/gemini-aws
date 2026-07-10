from app.providers.kubernetes.auth import KubernetesAuth

class ClusterHealth:
    def __init__(self, auth: KubernetesAuth):
        self.auth = auth
        self.api = auth.core_v1

    def is_healthy(self) -> bool:
        try:
            # Check if we can list nodes
            self.api.list_node(limit=1)
            return True
        except Exception:
            return False
