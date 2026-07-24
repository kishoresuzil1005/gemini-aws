# knowledge/relationships/relationship_exceptions.py
"""Custom exceptions for the Relationship Catalog."""

class RelationshipError(Exception):
    """Base exception for Relationship Catalog operations."""
    pass

class CircularDependencyError(RelationshipError):
    """Raised when a relationship cycle is detected."""
    pass

class InvalidRelationshipTypeError(RelationshipError):
    """Raised when an unclassified/unknown relationship type is submitted."""
    pass

class RelationshipNotFoundError(RelationshipError):
    """Raised when querying a relationship that does not exist."""
    pass
