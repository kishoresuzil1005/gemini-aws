from app.core.logging import get_logger
logger = get_logger(__name__)
from kubernetes import client, config

class KubernetesClientManager:
    """
    Centralized manager for Kubernetes Python SDK.
    """
    def __init__(self):
        try:
            config.load_kube_config()
        except Exception:
            try:
                config.load_incluster_config()
            except Exception as e:
                logger.debug(f"[KubernetesClientManager] Failed to load config: {e}")
        
    def get_core_client(self):
        return client.CoreV1Api()
    
    def get_apps_client(self):
        return client.AppsV1Api()
