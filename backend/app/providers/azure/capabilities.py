from typing import Dict, List
from app.services.ai.assistant.multicloud.multicloud_models import GenericResourceType, GenericAction

class AzureCapabilities:
    """Matrix of supported Azure operations."""

    # Resource -> List of Supported Actions
    CAPABILITIES: Dict[GenericResourceType, List[GenericAction]] = {
        GenericResourceType.COMPUTE: [
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
        GenericResourceType.DATABASE: [
            GenericAction.START,
            GenericAction.STOP,
            GenericAction.BACKUP
        ]
    }

    @classmethod
    def supports(cls, resource: GenericResourceType, action: GenericAction) -> bool:
        resource_actions = cls.CAPABILITIES.get(resource, [])
        return action in resource_actions
