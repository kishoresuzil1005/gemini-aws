"""
Strict, strongly typed Pydantic v2 models and Enums for the Enterprise Analyzer Framework.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AnalyzerCategory(str, Enum):
    SECURITY = "SECURITY"
    COST = "COST"
    PERFORMANCE = "PERFORMANCE"
    ARCHITECTURE = "ARCHITECTURE"
    DEPENDENCY = "DEPENDENCY"
    COMPLIANCE = "COMPLIANCE"


class AnalyzerPriority(str, Enum):
    P0 = "P0" # Critical / Blocker
    P1 = "P1" # High Priority
    P2 = "P2" # Medium Priority
    P3 = "P3" # Low Priority / Informational


class CloudProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    KUBERNETES = "KUBERNETES"
    VMWARE = "VMWARE"
    TERRAFORM = "TERRAFORM"
    DOCKER = "DOCKER"
    ON_PREM = "ON_PREM"
    MULTI_CLOUD = "MULTI_CLOUD"


class AnalyzerCapability(str, Enum):
    GRAPH_TRAVERSAL = "GRAPH_TRAVERSAL"
    LOG_ANALYSIS = "LOG_ANALYSIS"
    METRIC_ANALYSIS = "METRIC_ANALYSIS"
    API_CALL = "API_CALL"
    STATIC_CODE_ANALYSIS = "STATIC_CODE_ANALYSIS"


class SupportedResource(str, Enum):
    COMPUTE = "COMPUTE"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"
    IAM = "IAM"
    ALL = "ALL"


class ExecutionMode(str, Enum):
    SYNC = "SYNC"
    ASYNC = "ASYNC"
    STREAMING = "STREAMING"
    DISTRIBUTED = "DISTRIBUTED"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationPriority(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    OPTIONAL = "OPTIONAL"


class FindingStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class ValidationResult(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    SKIPPED = "SKIPPED"


class AnalyzerStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"
    NO_DATA = "NO_DATA"
    TIMEOUT = "TIMEOUT"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnalyzerMetadata(BaseModel):
    """Canonical identity and configuration description of an analyzer."""
    id: str = Field(..., description="Unique identifier (e.g., 'aws_security_analyzer').")
    name: str = Field(..., description="Human-readable name.")
    description: str = Field(..., description="Detailed description of capabilities.")
    version: str = Field(..., description="Semantic version (e.g., '1.0.0').")
    author: str = Field(default="system", description="Author or team responsible.")
    
    category: AnalyzerCategory = Field(..., description="Primary category.")
    priority: AnalyzerPriority = Field(default=AnalyzerPriority.P2, description="Execution priority.")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.SYNC, description="Supported execution model.")
    provider: CloudProvider = Field(default=CloudProvider.MULTI_CLOUD, description="Primary cloud provider.")
    
    supported_clouds: List[CloudProvider] = Field(default_factory=list, description="Clouds this analyzer can inspect.")
    supported_resources: List[SupportedResource] = Field(default_factory=list, description="Resources this analyzer supports.")
    supported_capabilities: List[AnalyzerCapability] = Field(default_factory=list, description="Capabilities required/used.")
    
    minimum_framework_version: str = Field(default="1.0.0", description="Min version of the engine required.")
    enabled: bool = Field(default=True, description="Whether this analyzer is enabled in the registry.")
    experimental: bool = Field(default=False, description="Flag for beta analyzers.")
    deprecated: bool = Field(default=False, description="Flag for sunsetting analyzers.")
    
    tags: List[str] = Field(default_factory=list, description="Searchable tags.")
    dependencies: List[str] = Field(default_factory=list, description="IDs of other analyzers required to run first.")
    documentation_url: Optional[str] = Field(default=None, description="URL to runbook or docs.")
    configuration_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for custom configs.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional opaque metadata.")


class AnalyzerConfiguration(BaseModel):
    """Immutable configuration for an analyzer execution."""
    cpu_threshold: float = Field(default=90.0, description="CPU usage threshold.")
    memory_threshold: float = Field(default=90.0, description="Memory usage threshold.")
    latency_threshold: float = Field(default=1000.0, description="Latency threshold in ms.")
    traversal_depth: int = Field(default=3, description="Maximum graph traversal depth.")
    traversal_timeout: float = Field(default=5.0, description="Maximum seconds for traversal.")
    max_nodes: int = Field(default=10000, description="Maximum nodes to process.")
    max_edges: int = Field(default=50000, description="Maximum edges to process.")
    idle_days: int = Field(default=14, description="Days to consider a resource idle.")
    backup_days: int = Field(default=7, description="Required backup retention in days.")
    blast_radius_threshold: int = Field(default=10, description="Threshold for critical blast radius.")

    class Config:
        frozen = True


class AnalyzerContext(BaseModel):
    """Strongly typed context containing only references to domain objects."""
    graph: Optional[Dict[str, Any]] = Field(default=None, description="Graph topology data.")
    inventory: Optional[Dict[str, Any]] = Field(default=None, description="Cloud inventory data.")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="CloudWatch/Metrics data.")
    policies: Optional[Dict[str, Any]] = Field(default=None, description="IAM or Security Policies.")
    topology: Optional[Dict[str, Any]] = Field(default=None, description="Network topology.")
    relationships: Optional[Dict[str, Any]] = Field(default=None, description="Resource relationships.")
    execution_context: Optional[Dict[str, Any]] = Field(default=None, description="Current execution metadata.")
    previous_results: Optional[Dict[str, Any]] = Field(default=None, description="Results from upstream analyzers.")
    validation_messages: List[str] = Field(default_factory=list, description="Context validation errors/warnings.")
    configuration: AnalyzerConfiguration = Field(default_factory=AnalyzerConfiguration, description="Immutable configuration thresholds.")


class Evidence(BaseModel):
    """Concrete evidence linking a finding to real cloud data."""
    resource_id: str = Field(..., description="ID of the resource.")
    resource_type: str = Field(..., description="Type of the resource.")
    attribute: str = Field(..., description="The attribute that triggered the finding.")
    actual_value: str = Field(..., description="The actual value found.")
    expected_value: str = Field(..., description="The expected or safe value.")
    source: str = Field(default="Analyzer", description="Source of the evidence.")
    timestamp: str = Field(default="", description="Time the evidence was collected.")
    confidence: Confidence = Field(default=Confidence.UNKNOWN, description="Confidence in the evidence.")


class AnalyzerFinding(BaseModel):
    """Deterministic finding generated by an analyzer."""
    id: str = Field(..., description="Unique ID for this finding instance.")
    title: str = Field(..., description="Short descriptive title.")
    description: str = Field(..., description="Detailed explanation.")
    resource_id: str = Field(..., description="ID of the affected resource.")
    resource_type: SupportedResource = Field(..., description="Type of the affected resource.")
    severity: Severity = Field(default=Severity.LOW, description="Severity of the finding.")
    status: FindingStatus = Field(default=FindingStatus.OPEN, description="Current status of the finding.")
    
    # New Optional Enterprise Fields
    root_cause: Optional[str] = Field(default=None, description="Identified root cause.")
    business_impact: Optional[str] = Field(default=None, description="Business impact explanation.")
    technical_impact: Optional[str] = Field(default=None, description="Technical impact explanation.")
    risk_level: Optional[RiskLevel] = Field(default=None, description="Calculated risk level.")
    confidence: Optional[Confidence] = Field(default=None, description="Confidence in the finding.")
    evidence: List[Evidence] = Field(default_factory=list, description="Concrete evidence blocks.")
    evidence_links: List[str] = Field(default_factory=list, description="Links to external evidence/dashboards.")
    remediation_difficulty: Optional[str] = Field(default=None, description="Estimated difficulty to fix.")
    compliance_framework: Optional[str] = Field(default=None, description="Associated compliance framework.")
    cve: Optional[str] = Field(default=None, description="Associated CVE if applicable.")
    tags: List[str] = Field(default_factory=list, description="Searchable tags.")
    labels: List[str] = Field(default_factory=list, description="Categorization labels.")
    created_time: Optional[str] = Field(default=None, description="Timestamp of finding creation.")
    updated_time: Optional[str] = Field(default=None, description="Timestamp of last update.")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw evidence data.")


class AnalyzerRecommendation(BaseModel):
    """Actionable recommendation resulting from an analysis."""
    title: str = Field(..., description="Short descriptive title.")
    description: str = Field(..., description="Detailed remediation instructions.")
    priority: RecommendationPriority = Field(default=RecommendationPriority.OPTIONAL, description="Remediation urgency.")
    estimated_effort: str = Field(default="Unknown", description="Effort to implement (e.g., 'Low', 'High').")
    
    # New Optional Enterprise Fields
    automation_possible: Optional[bool] = Field(default=None, description="Can this be automated?")
    automation_script: Optional[str] = Field(default=None, description="Terraform or CLI script to fix.")
    estimated_savings: Optional[float] = Field(default=None, description="Estimated monthly savings in USD.")
    estimated_risk_reduction: Optional[str] = Field(default=None, description="Estimated risk reduction metric.")
    estimated_downtime: Optional[str] = Field(default=None, description="Estimated downtime required to fix.")
    confidence: Optional[Confidence] = Field(default=None, description="Confidence in this recommendation.")
    affected_resources: List[str] = Field(default_factory=list, description="List of resources affected by this fix.")
    approval_required: Optional[bool] = Field(default=None, description="Does this fix require manual approval?")
    rollback_available: Optional[bool] = Field(default=None, description="Can this fix be rolled back?")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional opaque metadata.")


class ScoreBase(BaseModel):
    score: int = Field(default=0, description="The calculated score (0-100).")
    weight: float = Field(default=1.0, description="Weight of this score in overall calculations.")
    reason: str = Field(default="", description="Reasoning for this score.")
    confidence: Confidence = Field(default=Confidence.UNKNOWN, description="Confidence in this score.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional opaque metadata.")


class SecurityScore(ScoreBase): pass
class CostScore(ScoreBase): pass
class PerformanceScore(ScoreBase): pass
class ArchitectureScore(ScoreBase): pass
class DependencyScore(ScoreBase): pass


class OverallScore(ScoreBase):
    security: Optional[SecurityScore] = Field(default=None)
    cost: Optional[CostScore] = Field(default=None)
    performance: Optional[PerformanceScore] = Field(default=None)
    architecture: Optional[ArchitectureScore] = Field(default=None)
    dependency: Optional[DependencyScore] = Field(default=None)


class AnalyzerResult(BaseModel):
    """Complete output of an analyzer execution."""
    analyzer_id: str = Field(..., description="ID of the analyzer that produced this result.")
    validation_status: ValidationResult = Field(default=ValidationResult.VALID, description="Context validation result.")
    summary: str = Field(default="", description="High-level summary.")
    score: int = Field(default=100, description="Health or compliance score (0-100).")
    findings: List[AnalyzerFinding] = Field(default_factory=list, description="Specific deterministic findings.")
    recommendations: List[AnalyzerRecommendation] = Field(default_factory=list, description="Actionable recommendations.")
    execution_time_ms: float = Field(default=0.0, description="Execution duration in milliseconds.")
    
    # New Optional Enterprise Fields
    execution_status: AnalyzerStatus = Field(default=AnalyzerStatus.SUCCESS, description="Status of the analyzer execution.")
    validation_messages: List[str] = Field(default_factory=list, description="Messages from the validation phase.")
    resources_examined: int = Field(default=0, description="Number of resources examined.")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings during execution.")
    errors: List[str] = Field(default_factory=list, description="Fatal errors during execution.")
    confidence: Confidence = Field(default=Confidence.UNKNOWN, description="Overall confidence in this result.")
    evidence: List[Evidence] = Field(default_factory=list, description="Global evidence blocks.")
    detailed_score: Optional[OverallScore] = Field(default=None, description="Detailed breakdown of the score.")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution telemetry or opaque data.")
