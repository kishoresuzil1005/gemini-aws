"""
Pure Domain Models for the Enterprise Compliance Engine.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
# Reuse Security Models for input bridging
from app.services.ai.analyzers.engines.security.security_models import (
    ComplianceFramework, SecurityFinding, Severity
)

class ComplianceStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"
    MANUAL = "MANUAL"

class ControlSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class FrameworkVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    version: str
    year: str

class ComplianceEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    resource_id: str
    resource_type: str
    status: ComplianceStatus
    finding_id: Optional[str] = None
    reason: str

class ComplianceControl(BaseModel):
    model_config = ConfigDict(frozen=True)
    control_id: str = Field(..., description="E.g., CIS-1.2")
    title: str
    description: str
    severity: ControlSeverity
    status: ComplianceStatus
    evidence: List[ComplianceEvidence] = Field(default_factory=list)

class ComplianceRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)
    requirement_id: str = Field(..., description="E.g., CIS Identity and Access Management")
    title: str
    description: str
    controls: List[ComplianceControl] = Field(default_factory=list)
    status: ComplianceStatus

class ControlStatistics(BaseModel):
    model_config = ConfigDict(frozen=True)
    total: int = 0
    passed: int = 0
    failed: int = 0
    warning: int = 0
    skipped: int = 0
    manual: int = 0

class CoverageSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    percentage: float = 0.0
    evaluated_resources: int = 0

class ComplianceScore(BaseModel):
    model_config = ConfigDict(frozen=True)
    score: float = 0.0  # 0 to 100
    grade: str = "F"

class FrameworkStatistics(BaseModel):
    model_config = ConfigDict(frozen=True)
    controls: ControlStatistics
    coverage: CoverageSummary
    score: ComplianceScore
    severity_distribution: Dict[ControlSeverity, int] = Field(default_factory=dict)

class ComplianceResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    framework: ComplianceFramework
    version: FrameworkVersion
    requirements: List[ComplianceRequirement] = Field(default_factory=list)
    statistics: FrameworkStatistics

class ComplianceSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    executive_summary: str
    total_frameworks_evaluated: int
    overall_score: float
    global_statistics: ControlStatistics
    trend_placeholder: str = "TBD"

class ComplianceReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    report_id: str
    timestamp: float
    summary: ComplianceSummary
    results: List[ComplianceResult] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
