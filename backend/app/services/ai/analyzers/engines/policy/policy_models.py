"""
Domain Models for the Enterprise Policy Engine.
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from app.services.ai.analyzers.engines.security.security_models import Severity, SecurityCategory, RuleStatus

class PackStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    EXPERIMENTAL = "EXPERIMENTAL"

class EnvironmentType(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    QA = "QA"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    STARTUP = "STARTUP"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"
    FINANCIAL = "FINANCIAL"
    HEALTHCARE = "HEALTHCARE"

class FeatureFlag(BaseModel):
    model_config = ConfigDict(frozen=True)
    rule_id: str
    status: RuleStatus

class RuleOverride(BaseModel):
    model_config = ConfigDict(frozen=True)
    rule_id: str
    severity_override: Optional[Severity] = None
    category_override: Optional[SecurityCategory] = None
    priority_override: Optional[int] = None
    tags_add: List[str] = Field(default_factory=list)
    tags_remove: List[str] = Field(default_factory=list)

class PackVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    version: str
    min_engine_version: str

class PackDependency(BaseModel):
    model_config = ConfigDict(frozen=True)
    pack_id: str
    min_version: str

class PackMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    name: str
    description: str
    version: PackVersion
    status: PackStatus = PackStatus.ACTIVE
    dependencies: List[PackDependency] = Field(default_factory=list)

class RuleConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled_rules: List[str] = Field(default_factory=list)
    disabled_rules: List[str] = Field(default_factory=list)

class PolicyPack(BaseModel):
    """
    A discrete collection of rules and overrides (e.g., CIS Pack, Enterprise Pack).
    """
    model_config = ConfigDict(frozen=True)
    metadata: PackMetadata
    configuration: RuleConfiguration
    overrides: List[RuleOverride] = Field(default_factory=list)
    feature_flags: List[FeatureFlag] = Field(default_factory=list)

class EnvironmentProfile(BaseModel):
    """
    A profile mapping an environment (e.g. PRODUCTION) to a set of active packs.
    """
    model_config = ConfigDict(frozen=True)
    environment: EnvironmentType
    active_packs: List[str] = Field(default_factory=list)
    global_overrides: List[RuleOverride] = Field(default_factory=list)

class ExecutionProfile(BaseModel):
    """
    The finalized, fully resolved state produced by the Policy Engine.
    Consumed directly by the SecurityAnalyzer.
    """
    model_config = ConfigDict(frozen=True)
    environment: EnvironmentType
    active_rules: set[str] = Field(default_factory=set)
    rule_overrides: Dict[str, RuleOverride] = Field(default_factory=dict)
    rule_statuses: Dict[str, RuleStatus] = Field(default_factory=dict)

class PackStatistics(BaseModel):
    model_config = ConfigDict(frozen=True)
    total_packs_loaded: int
    total_rules_enabled: int
    total_overrides_applied: int
    total_feature_flags_applied: int

class PackSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    active_packs: List[str]
    statistics: PackStatistics
