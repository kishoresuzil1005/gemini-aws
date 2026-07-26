# knowledge/relationships/relationship_exceptions.py
"""Custom exceptions for the Relationship Catalog."""

class RelationshipError(Exception):
    """Base exception for Relationship Catalog operations."""
    ...

class CircularDependencyError(RelationshipError):
    """Raised when a relationship cycle is detected."""
    ...

class InvalidRelationshipTypeError(RelationshipError):
    """Raised when an unclassified/unknown relationship type is submitted."""
    ...

class RelationshipNotFoundError(RelationshipError):
    """Raised when querying a relationship that does not exist."""
    ...
