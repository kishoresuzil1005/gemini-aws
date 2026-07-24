# knowledge/catalog/catalog_exceptions.py
"""Custom exceptions for the Resource Catalog."""

class CatalogError(Exception):
    """Base exception for Catalog operations."""
    pass

class ResourceNotFoundError(CatalogError):
    """Raised when querying a resource that does not exist in the catalog."""
    pass

class CatalogValidationError(CatalogError):
    """Raised when an entry fails schema validation before insertion."""
    pass
