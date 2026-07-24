# knowledge/validation/validation_result.py
"""Data structures representing the outcome of a single validation check."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ValidationCheckResult(BaseModel):
    """Represents the atomic result of a specific validation rule."""
    validator_name: str
    passed: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
