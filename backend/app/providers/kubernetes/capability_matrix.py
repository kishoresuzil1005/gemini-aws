from typing import Dict, List
from app.services.ai.assistant.multicloud.multicloud_models import GenericResourceType, GenericAction

class KubernetesCapabilities:
    """Matrix of supported Kubernetes operations."""

    CAPABILITIES: Dict[GenericResourceType, List[GenericAction]] = {
        GenericResourceType.COMPUTE: [
            GenericAction.CREATE,
            GenericAction.START,
            GenericAction.STOP,
            GenericAction.RESTART,
            GenericAction.DELETE,
            GenericAction.RESIZE
        ],
        GenericResourceType.STORAGE: [
            GenericAction.CREATE,
            GenericAction.DELETE
        ],
        GenericResourceType.NETWORK: [
            GenericAction.CREATE,
            GenericAction.DELETE
        ],
        GenericResourceType.SECURITY: [
            GenericAction.CREATE,
            GenericAction.DELETE
        ]
    }

    @classmethod
    def supports(cls, resource: GenericResourceType, action: GenericAction) -> bool:
        resource_actions = cls.CAPABILITIES.get(resource, [])
        return action in resource_actions
