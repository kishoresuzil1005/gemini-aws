# knowledge/validation/validation_exceptions.py
"""Custom exceptions for the Validation Engine."""


class ValidationError(Exception):
    """Base exception for all validation errors."""
    pass


class FatalValidationError(ValidationError):
    """Raised when a validation error is severe enough to halt the entire pipeline."""
    pass


class RetryableValidationError(ValidationError):
    """Raised when a validation check fails due to a transient issue and can be retried."""
    pass


class IntegrityError(FatalValidationError):
    """Raised when the snapshot's checksum, size, or file existence checks fail."""
    pass
