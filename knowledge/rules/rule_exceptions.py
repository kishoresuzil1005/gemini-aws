# knowledge/rules/rule_exceptions.py
"""Custom exceptions for the Rule Catalog."""

class RuleError(Exception):
    """Base exception for Rule Catalog operations."""
    pass

class RuleNotFoundError(RuleError):
    """Raised when querying a rule that does not exist."""
    pass

class RuleValidationError(RuleError):
    """Raised when a rule fails schema validation before insertion."""
    pass

class InvalidStateTransitionError(RuleError):
    """Raised when an illegal lifecycle transition is attempted (e.g. ARCHIVED -> PUBLISHED)."""
    pass
