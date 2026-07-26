# knowledge/rules/rule_exceptions.py
"""Custom exceptions for the Rule Catalog."""

class RuleError(Exception):
    """Base exception for Rule Catalog operations."""
    ...

class RuleNotFoundError(RuleError):
    """Raised when querying a rule that does not exist."""
    ...

class RuleValidationError(RuleError):
    """Raised when a rule fails schema validation before insertion."""
    ...

class InvalidStateTransitionError(RuleError):
    """Raised when an illegal lifecycle transition is attempted (e.g. ARCHIVED -> PUBLISHED)."""
    ...
