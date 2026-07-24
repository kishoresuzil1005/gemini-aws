# knowledge/validation/validation_report.py
"""Defines the standard JSON schema for the output of the Validation Engine."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .validation_result import ValidationCheckResult


class ValidationReportChecks(BaseModel):
    passed: int = 0
    failed: int = 0
    warnings: int = 0


class ValidationWarning(BaseModel):
    validator: str
    message: str


class ValidationReport(BaseModel):
    """The canonical schema for the Validation Report emitted by the engine."""
    validation_id: str
    snapshot_id: str
    provider: str
    knowledge_source: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    duration_ms: int = 0
    status: str = Field(..., description="PASSED, FAILED, or REJECTED")
    quality_score: float = 0.0
    checks: ValidationReportChecks = Field(default_factory=ValidationReportChecks)
    errors: List[str] = Field(default_factory=list)
    warnings: List[ValidationWarning] = Field(default_factory=list)
    detailed_results: List[ValidationCheckResult] = Field(default_factory=list, exclude=True) # Optional for debugging
