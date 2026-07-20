"""Exception hierarchy for the AI Context Engine."""

class ContextEngineError(Exception):
    """Base class for all Context Engine errors."""

class ResourceNotFoundError(ContextEngineError):
    pass

class ProviderError(ContextEngineError):
    pass

class CacheError(ContextEngineError):
    pass

class ContextBuildError(ContextEngineError):
    pass
