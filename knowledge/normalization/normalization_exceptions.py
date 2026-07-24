# knowledge/normalization/normalization_exceptions.py
"""Custom exceptions for the Normalization Engine."""

class NormalizationError(Exception):
    """Base exception for normalization issues."""
    pass

class UnsupportedProviderError(NormalizationError):
    """Raised when a candidate originates from an unknown provider."""
    pass

class MappingError(NormalizationError):
    """Raised when canonical mapping fails due to schema mismatch."""
    pass

class PartialNormalizationError(NormalizationError):
    """Raised when some candidates succeed but others fail."""
    pass
