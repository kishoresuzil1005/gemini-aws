from typing import Dict, List
from pydantic import BaseModel
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class ProviderMetadata(BaseModel):
    display_name: str
    regions: List[str]
    supports_tags: bool
    supports_cost_api: bool
    supports_iam: bool
    supports_kubernetes: bool

PROVIDER_METADATA: Dict[CloudProvider, ProviderMetadata] = {
    CloudProvider.AWS: ProviderMetadata(
        display_name="Amazon Web Services",
        regions=["us-east-1", "us-west-2", "eu-west-1"],
        supports_tags=True,
        supports_cost_api=True,
        supports_iam=True,
        supports_kubernetes=True
    ),
    CloudProvider.AZURE: ProviderMetadata(
        display_name="Microsoft Azure",
        regions=["eastus", "westus", "northeurope"],
        supports_tags=True,
        supports_cost_api=True,
        supports_iam=True,
        supports_kubernetes=True
    ),
    CloudProvider.GCP: ProviderMetadata(
        display_name="Google Cloud Platform",
        regions=["us-central1", "europe-west1"],
        supports_tags=True,
        supports_cost_api=True,
        supports_iam=True,
        supports_kubernetes=True
    ),
    CloudProvider.KUBERNETES: ProviderMetadata(
        display_name="Kubernetes",
        regions=["local", "cluster"],
        supports_tags=True,
        supports_cost_api=False,
        supports_iam=False,
        supports_kubernetes=True
    )
}
