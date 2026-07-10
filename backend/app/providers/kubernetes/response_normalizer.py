from typing import Any
from app.providers.common.models import ProviderResponse

class KubernetesResponseNormalizer:
    """Normalizes raw Kubernetes Python SDK responses into a generic format for the AI."""
    
    @staticmethod
    def normalize(raw_response: Any) -> ProviderResponse:
        if raw_response is None:
            return ProviderResponse(success=True, data={"status": "completed_no_data"})
            
        # The python kubernetes client models have to_dict()
        if hasattr(raw_response, "to_dict"):
            data = raw_response.to_dict()
        elif isinstance(raw_response, dict):
            data = raw_response
        else:
            data = {"raw_output": str(raw_response)}
            
        return ProviderResponse(success=True, data=data)

    @staticmethod
    def normalize_error(error_message: str) -> ProviderResponse:
        return ProviderResponse(success=False, error=error_message)
