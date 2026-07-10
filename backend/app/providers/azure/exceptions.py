from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from app.providers.common.errors import (
    ProviderError,
    ResourceNotFoundError,
    AuthenticationError,
    PermissionDeniedError,
    QuotaExceededError
)

def map_azure_exception(e: Exception) -> Exception:
    """Maps Azure-specific HttpResponseErrors to generic ProviderErrors."""
    if isinstance(e, HttpResponseError):
        if e.status_code == 401:
            return AuthenticationError(f"Azure authentication failed: {e.message}")
        if e.status_code == 403:
            return PermissionDeniedError(f"Azure permission denied: {e.message}")
        if e.status_code == 404:
            return ResourceNotFoundError(f"Azure resource not found: {e.message}")
        if e.status_code == 429:
            return QuotaExceededError(f"Azure quota exceeded: {e.message}")
    
    # Return as generic if unmapped
    return ProviderError(str(e))
