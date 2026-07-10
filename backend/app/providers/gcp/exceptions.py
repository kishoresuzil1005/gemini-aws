from google.api_core.exceptions import GoogleAPIError, NotFound, PermissionDenied, ResourceExhausted, Unauthenticated

from app.providers.common.errors import (
    ProviderError,
    ResourceNotFoundError,
    AuthenticationError,
    PermissionDeniedError,
    QuotaExceededError
)

def map_gcp_exception(e: Exception) -> Exception:
    """Maps GCP-specific GoogleAPIErrors to generic ProviderErrors."""
    if isinstance(e, Unauthenticated):
        return AuthenticationError(f"GCP authentication failed: {str(e)}")
    if isinstance(e, PermissionDenied):
        return PermissionDeniedError(f"GCP permission denied: {str(e)}")
    if isinstance(e, NotFound):
        return ResourceNotFoundError(f"GCP resource not found: {str(e)}")
    if isinstance(e, ResourceExhausted):
        return QuotaExceededError(f"GCP quota exceeded: {str(e)}")
        
    # If we catch a generic GoogleAPIError that we haven't explicitly mapped
    if isinstance(e, GoogleAPIError):
        return ProviderError(f"GCP API Error: {str(e)}")
    
    # Return as generic if completely unmapped
    return ProviderError(str(e))
