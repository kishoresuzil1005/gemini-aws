class ProviderError(Exception):
    """Base generic error for the AI platform."""
    pass

class ResourceNotFoundError(ProviderError):
    pass

class AuthenticationError(ProviderError):
    pass

class PermissionDeniedError(ProviderError):
    pass

class QuotaExceededError(ProviderError):
    pass

class TimeoutError(ProviderError):
    pass

class AlreadyExistsError(ProviderError):
    pass

class RateLimitedError(ProviderError):
    pass
