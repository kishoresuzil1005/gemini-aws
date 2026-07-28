# exceptions/analyzer_exceptions.py
"""Domain-specific exceptions for Analyzers."""

class KnowledgeNotFoundError(Exception):
    """Raised when an analyzer requests knowledge that does not exist."""
    pass

class KnowledgeServiceError(Exception):
    """Raised when there is an issue communicating with the Knowledge Service."""
    pass
