from typing import Any, Dict
from app.providers.azure.models import ProviderResponse

class AzureResponseNormalizer:
    """Normalizes raw Azure SDK responses into a generic format for the AI."""
    
    @staticmethod
    def normalize(raw_response: Any) -> ProviderResponse:
        """
        Takes a raw Azure response object (or dict) and normalizes it.
        """
        if raw_response is None:
            return ProviderResponse(success=True, data={"status": "completed_no_data"})
            
        # If it's an Azure model, convert to dict. Many SDK models have as_dict().
        if hasattr(raw_response, 'as_dict'):
            data = raw_response.as_dict()
        elif isinstance(raw_response, dict):
            data = raw_response
        else:
            # Fallback for strings or lists
            data = {"raw_output": str(raw_response)}
            
        return ProviderResponse(success=True, data=data)

    @staticmethod
    def normalize_error(error_message: str) -> ProviderResponse:
        """Creates a normalized failure response."""
        return ProviderResponse(success=False, error=error_message)
