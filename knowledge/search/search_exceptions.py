# knowledge/search/search_exceptions.py
"""Custom exception hierarchy for the Search Engine."""

class SearchError(Exception):
    """Base exception for all search related errors."""
    pass

class IndexError(SearchError):
    """Raised when the underlying index cannot be accessed or is corrupted."""
    pass

class QueryError(SearchError):
    """Raised for malformed queries or unsupported operations."""
    pass
