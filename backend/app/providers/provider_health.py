from pydantic import BaseModel
from typing import Dict
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class ProviderHealthStatus(BaseModel):
    is_connected: bool
    credentials_valid: bool
    health_score: int
    message: str

class ProviderHealthEngine:
    def __init__(self):
        # Mocks health checks for all providers
        self.health_states: Dict[CloudProvider, ProviderHealthStatus] = {
            CloudProvider.AWS: ProviderHealthStatus(is_connected=True, credentials_valid=True, health_score=100, message="Healthy"),
            CloudProvider.AZURE: ProviderHealthStatus(is_connected=True, credentials_valid=True, health_score=100, message="Healthy"),
            CloudProvider.GCP: ProviderHealthStatus(is_connected=True, credentials_valid=True, health_score=100, message="Healthy")
        }

    def check_health(self, provider: CloudProvider) -> ProviderHealthStatus:
        # A real system would attempt a lightweight API call (e.g. sts.get_caller_identity in AWS)
        return self.health_states.get(
            provider, 
            ProviderHealthStatus(is_connected=False, credentials_valid=False, health_score=0, message="Unknown Provider")
        )
