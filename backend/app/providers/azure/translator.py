from typing import Dict, Any, Tuple
from app.services.ai.assistant.multicloud.multicloud_models import GenericAction, GenericResourceType, TranslatedActionPayload

class AzureTranslator:
    """Translates generic MultiCloud requests into Azure SDK method names and kwargs."""
    
    def translate(self, payload: TranslatedActionPayload) -> Tuple[str, Dict[str, Any]]:
        """
        Returns a tuple of (azure_method_name, kwargs) based on the translated payload.
        This provides a final mapping from generic terminology to exact Azure SDK arguments.
        """
        method_name = payload.api_call
        kwargs = payload.payload.copy()
        
        # We can add explicit kwargs re-mapping here if necessary.
        # E.g., if generic payload says "resource_id", we might map to "resource_group_name" and "vm_name"
        
        # Example logic for Compute instances
        if "resource_id" in kwargs:
            resource_id = kwargs.pop("resource_id")
            # Usually Azure resource IDs look like: /subscriptions/sub-id/resourceGroups/rg-name/providers/...
            parts = resource_id.split("/")
            if len(parts) >= 9:
                rg_name = parts[4]
                resource_name = parts[8]
                kwargs["resource_group_name"] = rg_name
                if "virtualMachines" in resource_id:
                    kwargs["vm_name"] = resource_name
                    
        return method_name, kwargs
