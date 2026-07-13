from typing import Dict, List
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericResourceType, GenericAction

class UnsupportedCapabilityError(Exception):
    pass

class ProviderCapability:
    """Matrix of supported operations per cloud provider."""

    # Provider -> Resource -> List of Supported Actions
    CAPABILITIES: Dict[CloudProvider, Dict[GenericResourceType, List[GenericAction]]] = {
        CloudProvider.AWS: {
            GenericResourceType.COMPUTE: [GenericAction.START, GenericAction.STOP, GenericAction.RESTART, GenericAction.DELETE],
            GenericResourceType.DATABASE: [GenericAction.START, GenericAction.STOP, GenericAction.BACKUP]
        },
        CloudProvider.AZURE: {
            GenericResourceType.COMPUTE: [GenericAction.START, GenericAction.STOP, GenericAction.RESTART, GenericAction.DELETE],
            GenericResourceType.DATABASE: [GenericAction.START, GenericAction.STOP, GenericAction.BACKUP]
        },
        CloudProvider.GCP: {
            GenericResourceType.COMPUTE: [GenericAction.START, GenericAction.STOP, GenericAction.RESTART, GenericAction.DELETE],
            GenericResourceType.DATABASE: [GenericAction.START, GenericAction.STOP, GenericAction.BACKUP]
        }
    }

    def supports_action(self, provider: CloudProvider, resource: GenericResourceType, action: GenericAction) -> bool:
        provider_caps = self.CAPABILITIES.get(provider, {})
        resource_actions = provider_caps.get(resource, [])
        return action in resource_actions

    def ensure_capability(self, provider: CloudProvider, resource: GenericResourceType, action: GenericAction):
        if not self.supports_action(provider, resource, action):
            raise UnsupportedCapabilityError(
                f"Provider {provider.value} does not support action {action.value} on {resource.value}."
            )