from typing import Dict, Any
from .aws.discovery.aws_discovery import AWSDiscoveryEngine
from .azure.discovery.azure_discovery import AzureDiscoveryEngine
from .gcp.discovery.gcp_discovery import GCPDiscoveryEngine
from .kubernetes.discovery.k8s_discovery import K8sDiscoveryEngine

class CrossCloudDiscovery:
    """
    The master orchestrator that triggers and merges discovery pipelines 
    across AWS, Azure, GCP, and Kubernetes simultaneously. (Epic 4)
    """
    def __init__(self, aws_client, azure_client, gcp_client, k8s_client):
        self.aws = AWSDiscoveryEngine(aws_client)
        self.azure = AzureDiscoveryEngine(azure_client)
        self.gcp = GCPDiscoveryEngine(gcp_client)
        self.k8s = K8sDiscoveryEngine(k8s_client)

    def discover_all_clouds(self) -> Dict[str, Any]:
        print("[CrossCloudDiscovery] Initiating parallel discovery across all clouds...")
        return {
            "aws": self.aws.run_full_discovery(),
            "azure": self.azure.run_full_discovery(),
            "gcp": self.gcp.run_full_discovery(),
            "kubernetes": self.k8s.run_full_discovery()
        }
