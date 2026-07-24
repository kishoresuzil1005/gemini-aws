"""
Pure Domain Models for the Security Engine.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, constr
from app.services.ai.analyzers.base.analyzer_models import Severity, CloudProvider

class ComplianceFramework(str, Enum):
    CIS = "CIS"
    NIST = "NIST"
    SOC2 = "SOC2"
    PCI_DSS = "PCI DSS"
    ISO27001 = "ISO27001"
    AWS_WELL_ARCHITECTED = "AWS Well Architected"

class SecurityDomain(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    KUBERNETES = "KUBERNETES"
    LINUX = "LINUX"
    WINDOWS = "WINDOWS"
    DOCKER = "DOCKER"
    GITHUB = "GITHUB"
    CICD = "CICD"
    TERRAFORM = "TERRAFORM"
    MULTI_CLOUD = "MULTI_CLOUD"

class SecurityCategory(str, Enum):
    IDENTITY = "IDENTITY"
    NETWORK = "NETWORK"
    COMPUTE = "COMPUTE"
    STORAGE = "STORAGE"
    DATABASE = "DATABASE"
    CONTAINER = "CONTAINER"
    KUBERNETES = "KUBERNETES"
    MONITORING = "MONITORING"
    ENCRYPTION = "ENCRYPTION"
    SECRETS = "SECRETS"
    LOGGING = "LOGGING"
    COMPLIANCE = "COMPLIANCE"
    GOVERNANCE = "GOVERNANCE"
    CONTAINERS = "CONTAINERS"
    RESILIENCE = "RESILIENCE"

class RuleStatus(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    AUDIT_ONLY = "AUDIT_ONLY"
    WARNING_ONLY = "WARNING_ONLY"

class RuleCapability(str, Enum):
    PREVENTIVE = "PREVENTIVE"
    DETECTIVE = "DETECTIVE"
    CORRECTIVE = "CORRECTIVE"
    INVESTIGATIVE = "INVESTIGATIVE"

class RuleMetadata(BaseModel):
    """
    Immutable metadata for a SecurityRule.
    """
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(..., description="E.g., AWS-S3-001")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version")
    name: str = Field(...)
    description: str = Field(...)
    
    # Classification
    provider: CloudProvider = Field(...)
    domain: SecurityDomain = Field(...)
    category: SecurityCategory = Field(...)
    capability: RuleCapability = Field(default=RuleCapability.DETECTIVE)
    severity: Severity = Field(...)
    
    # Lifecycle
    status: RuleStatus = Field(default=RuleStatus.ENABLED)
    created_version: str = Field(default="1.0.0")
    deprecated: bool = Field(default=False)
    experimental: bool = Field(default=False)
    
    # Meta
    owner: str = Field(default="SecurityOps")
    tags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    documentation_url: Optional[str] = Field(default=None)
    
    # Expanded per user request
    resource_types: List[str] = Field(default_factory=list)
    supported_clouds: List[CloudProvider] = Field(default_factory=list)
    frameworks: List[ComplianceFramework] = Field(default_factory=list)
    enabled_by_default: bool = Field(default=True)
    introduced_version: str = Field(default="1.0.0")
    last_updated: str = Field(default="1.0.0")

class Evidence(BaseModel):
    """
    Deterministic evidence to support APIs and future AI explanation layers.
    """
    model_config = ConfigDict(frozen=True)
    
    resource_id: str
    resource_name: Optional[str] = None
    resource_type: str
    
    expected: Any
    actual: Any
    reason: str
    
    path: Optional[str] = None
    property: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[float] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class SecurityFinding(BaseModel):
    """
    Deterministic result from a single Security Rule.
    Scoring is handled independently by the ScoringEngine.
    """
    rule_id: str = Field(...)
    rule_name: str = Field(...)
    resource_id: str = Field(...)
    resource_type: str = Field(...)
    category: SecurityCategory = Field(...)
    
    # Raw severity declared by the rule before blast-radius scaling
    base_severity: Severity = Field(...)
    
    # Detailed Context
    description: str = Field(...)
    root_cause: str = Field(...)
    technical_impact: str = Field(...)
    business_impact: str = Field(...)
    
    evidence: Evidence = Field(...)
    recommendation: str = Field(...)
    
    # Metadata
    automation_available: bool = Field(default=False)
    compliance_mapping: List[ComplianceFramework] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    timestamp: float = Field(default=0.0)
    confidence: str = Field(default="HIGH")
