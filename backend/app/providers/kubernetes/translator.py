from typing import Dict, Any, Tuple
from app.services.ai.assistant.multicloud.multicloud_models import TranslatedActionPayload

class KubernetesTranslator:
    """Translates generic MultiCloud requests into Kubernetes Python SDK method names and kwargs."""
    
    def translate(self, payload: TranslatedActionPayload) -> Tuple[str, Dict[str, Any]]:
        """
        Returns a tuple of (k8s_method_name, kwargs).
        """
        method_name = payload.api_call
        kwargs = payload.payload.copy()
        
        # Kubernetes API often requires 'name' and 'namespace' explicitly
        return method_name, kwargs
