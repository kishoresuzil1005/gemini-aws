from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import List, Dict, Any
from .k8s_client import KubernetesClientManager

class K8sClusterService:
    def __init__(self, client_manager: KubernetesClientManager):
        self.core_api = client_manager.get_core_client()
        self.apps_api = client_manager.get_apps_client()

    def list_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        logger.debug(f"[K8sClusterService] Discovering Pods in namespace '{namespace}'...")
        pods = []
        try:
            ret = self.core_api.list_namespaced_pod(namespace=namespace)
            for i in ret.items:
                pods.append({"name": i.metadata.name, "ip": i.status.pod_ip, "type": "K8s::Pod"})
        except Exception as e:
            logger.debug(f"[K8sClusterService] Skipping real API call, mock returning empty list due to: {e}")
        return pods

    def list_deployments(self, namespace: str = "default") -> List[Dict[str, Any]]:
        deployments = []
        try:
            ret = self.apps_api.list_namespaced_deployment(namespace=namespace)
            for i in ret.items:
                deployments.append({"name": i.metadata.name, "replicas": i.spec.replicas, "type": "K8s::Deployment"})
        except Exception:
            pass
        return deployments
