from typing import List, Dict
from pydantic import BaseModel
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class ProviderConnection(BaseModel):
    provider: CloudProvider
    account_id: str
    is_active: bool

class ProviderDiscovery:
    """Discovers connected cloud environments and active regions/subscriptions."""
    
    def __init__(self):
        # In a real system, this queries the database or secret manager for connected cloud credentials.
        self.connected_providers: Dict[CloudProvider, ProviderConnection] = {
            CloudProvider.AWS: ProviderConnection(provider=CloudProvider.AWS, account_id="123456789012", is_active=True),
            CloudProvider.AZURE: ProviderConnection(provider=CloudProvider.AZURE, account_id="sub-abc-123", is_active=True),
            CloudProvider.GCP: ProviderConnection(provider=CloudProvider.GCP, account_id="project-xyz-456", is_active=True)
        }

    def get_connected_providers(self) -> List[CloudProvider]:
        return [p.provider for p in self.connected_providers.values() if p.is_active]
        
    def is_provider_connected(self, provider: CloudProvider) -> bool:
        conn = self.connected_providers.get(provider)
        return conn is not None and conn.is_activ