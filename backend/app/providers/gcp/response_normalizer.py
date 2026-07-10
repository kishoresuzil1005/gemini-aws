from typing import Any
from app.providers.gcp.models import ProviderResponse

class GCPResponseNormalizer:
    """Normalizes raw GCP SDK responses into a generic format for the AI."""
    
    @staticmethod
    def normalize(raw_response: Any) -> ProviderResponse:
        """
        Takes a raw GCP response object (or dict) and normalizes it.
        """
        if raw_response is None:
            return ProviderResponse(success=True, data={"status": "completed_no_data"})
            
        # Many google SDK objects have a to_dict() or we can convert them via MessageToDict if protobuf
        if hasattr(raw_response, "to_dict"):
            data = raw_response.to_dict()
        elif hasattr(raw_response, "_pb"):
            from google.protobuf.json_format import MessageToDict
            data = MessageToDict(raw_response._pb)
        elif isinstance(raw_response, dict):
            data = raw_response
        else:
            data = {"raw_output": str(raw_response)}
            
        return ProviderResponse(success=True, data=data)

    @staticmethod
    def normalize_error(error_message: str) -> ProviderResponse:
        """Creates a normalized failure response."""
        return ProviderResponse(success=False, error=error_message)
