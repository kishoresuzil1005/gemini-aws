from typing import Dict, Any
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericAction, GenericResourceType, TranslatedActionPayload

class ActionTranslator:
    """Translates generic actions into provider-specific SDK payloads."""
    
    def translate(
        self, 
        provider: CloudProvider, 
        action: GenericAction, 
        resource_type: GenericResourceType, 
        resource_id: str, 
        parameters: Dict[str, Any]
    ) -> TranslatedActionPayload:
        
        api_call = ""
        payload = parameters.copy()
        
        # Simplified Mock Translation Logic
        if resource_type == GenericResourceType.COMPUTE and action == GenericAction.STOP:
            if provider == CloudProvider.AWS:
                api_call = "stop_instances"
                payload["InstanceIds"] = [resource_id]
            elif provider == CloudProvider.AZURE:
                api_call = "begin_deallocate"
                payload["vm_name"] = resource_id
            elif provider == CloudProvider.GCP:
                api_call = "instances.stop"
                payload["instance"] = resource_id
                
        elif resource_type == GenericResourceType.DATABASE and action == GenericAction.DELETE:
            if provider == CloudProvider.AWS:
                api_call = "delete_db_instance"
                payload["DBInstanceIdentifier"] = resource_id
                
        if not api_call:
            # Fallback for testing unmapped routes
            api_call = f"generic_{action.value.lower()}"
            payload["resource_id"] = resource_id

        return TranslatedActionPayload(
            provider=provider,
            api_call=api_call,
            payload=payload
        