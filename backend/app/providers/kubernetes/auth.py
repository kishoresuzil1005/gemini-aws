from kubernetes import config, client
import os
import logging

logger = logging.getLogger(__name__)

class KubernetesAuth:
    """Handles authentication for various Kubernetes environments."""
    
    def __init__(self):
        self._load_config()
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()
        self.storage_v1 = client.StorageV1Api()
        
    def _load_config(self):
        """Attempts to load in-cluster config, falling back to kubeconfig."""
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration.")
        except config.ConfigException:
            try:
                config.load_kube_config()
                logger.info("Loaded local kubeconfig.")
            except Exception as e:
                logger.warning(f"Failed to load kubernetes configuration: {e}")
