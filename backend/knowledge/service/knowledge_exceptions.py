# knowledge/service/knowledge_exceptions.py
"""Custom exceptions for the Knowledge Service layer."""

class ServiceError(Exception):
    """Base exception for Service operations."""
    ...

class QueryError(ServiceError):
    """Raised when an invalid query or malformed request is submitted."""
    ...

class ResourceNotFoundError(ServiceError):
    """Raised when an entity is not found via the service."""
    ...
