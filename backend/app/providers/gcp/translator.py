from typing import Dict, Any, Tuple
from app.services.ai.assistant.multicloud.multicloud_models import TranslatedActionPayload

class GCPTranslator:
    """Translates generic MultiCloud requests into GCP SDK method names and kwargs."""
    
    def translate(self, payload: TranslatedActionPayload) -> Tuple[str, Dict[str, Any]]:
        """
        Returns a tuple of (gcp_method_name, kwargs).
        """
        method_name = payload.api_call
        kwargs = payload.payload.copy()
        
        # We can implement GCP-specific mapping rules here (e.g. mapping fields from the parsed resource_id)
        # Often resource_parser will have already split the resource_id.
        return method_name, kwargs
