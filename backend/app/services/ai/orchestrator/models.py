"""
Phase 2 – Unified Resource Model
=================================
All context providers must return data conforming to these Pydantic models.
This guarantees a common schema across AWS, Azure, GCP, Kubernetes, and on-prem.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    KUBERNETES = "kubernetes"
    ONPREM = "onprem"
    UNKNOWN = "unknown"


class ResourceStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    TERMINATED = "terminated"
    PENDING = "pending"
    UNKNOWN = "unknown"


class ProviderPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProviderOutcome(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


class IntentCategory(str, Enum):
    HEALTH_CHECK = "health_check"
    COST_ANALYSIS = "cost_analysis"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE = "performance"
    RELATIONSHIP_QUERY = "relationship_query"
    REMEDIATION = "remediation"
    GENERAL = "general"


# ---------------------------------------------------------------------------
# Core Resource Model (Phase 2)
# ---------------------------------------------------------------------------

class ResourceRelationship(BaseModel):
    """Edge in the resource dependency graph."""
    resource_id: str
    relation_type: str                        # e.g. ROUTES_TO, DEPENDS_ON, CONTAINS
    direction: str = "outbound"               # inbound | outbound


class MetricPoint(BaseModel):
    """A single time-series data point."""
    timestamp: datetime
    value: float
    unit: str = ""


class SecurityFinding(BaseModel):
    """A security issue attached to a resource."""
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: str                             # CRITICAL | HIGH | MEDIUM | LOW | INFO
    title: str
    description: str
    remediation_hint: Optional[str] = None
    source: str = ""                          # guardduty | inspector | config | custom


class Resource(BaseModel):
    """
    Canonical representation of any cloud resource.

    All providers (inventory, graph, metrics, security, cost, docs)
    must map their output onto this model or a subclass.
    """
    id: str
    provider: CloudProvider = CloudProvider.UNKNOWN
    service: str                              # ec2, rds, lambda, s3, aks, …
    type: str                                 # instance, volume, bucket, alarm, …
    name: Optional[str] = None
    region: Optional[str] = None
    account_id: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    status: ResourceStatus = ResourceStatus.UNKNOWN
    created_at: Optional[datetime] = None

    # Relational data
    relationships: List[ResourceRelationship] = Field(default_factory=list)

    # Operational data (filled by providers)
    metrics: Dict[str, List[MetricPoint]] = Field(default_factory=dict)
    findings: List[SecurityFinding] = Field(default_factory=list)
    cost: Optional[float] = None              # USD / month
    owner: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)  # provider-specific raw data


# ---------------------------------------------------------------------------
# Intent & Reasoning Models (Phase 3 prep)
# ---------------------------------------------------------------------------

class CandidateQuery(BaseModel):
    """Structured output from the EntityExtractor."""
    raw_input: str
    tokens: List[str] = Field(default_factory=list)
    resource_ids: List[str] = Field(default_factory=list)   # explicit ARNs / IDs
    service_hints: List[str] = Field(default_factory=list)  # ec2, rds, …
    environment_hints: List[str] = Field(default_factory=list)  # prod, staging, …
    owner_hints: List[str] = Field(default_factory=list)
    tag_filters: Dict[str, str] = Field(default_factory=dict)


class ResolvedResource(BaseModel):
    """A resource candidate with a confidence score from the MultiSourceResolver."""
    resource: Resource
    confidence: float = 0.0            # 0.0 – 1.0
    source: str = ""                   # redis_cache | postgres | neo4j | aws_api | …


class ReasoningResult(BaseModel):
    """Output of the InfrastructureReasoningEngine (pure logic, no LLM)."""
    intent: IntentCategory = IntentCategory.GENERAL
    required_providers: List[str] = Field(default_factory=list)
    resource_query: CandidateQuery
    confidence: float = 0.0
    explanation: str = ""


# ---------------------------------------------------------------------------
# Provider Execution Models (Phase 6 prep)
# ---------------------------------------------------------------------------

class ProviderResult(BaseModel):
    """Standardised result returned by every context provider."""
    provider: str
    outcome: ProviderOutcome = ProviderOutcome.SUCCESS
    priority: ProviderPriority = ProviderPriority.MEDIUM
    confidence: float = 0.0
    completeness: float = 0.0
    freshness: float = 1.0
    latency_ms: int = 0
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ContextQualityScore(BaseModel):
    """Aggregate quality score across all provider results."""
    score: float = 0.0                  # 0.0 – 1.0
    providers_executed: List[str] = Field(default_factory=list)
    providers_skipped: List[str] = Field(default_factory=list)
    providers_failed: List[str] = Field(default_factory=list)
    target_reached: bool = False


# ---------------------------------------------------------------------------
# Unified Context (Phase 9 prep)
# ---------------------------------------------------------------------------

class UnifiedContext(BaseModel):
    """
    Final merged context payload sent to the PromptBuilder.
    Produced by the Aggregator after all providers have run.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resource: Optional[Resource] = None
    related_resources: List[Resource] = Field(default_factory=list)
    provider_results: List[ProviderResult] = Field(default_factory=list)
    quality: ContextQualityScore = Field(default_factory=ContextQualityScore)
    reasoning: Optional[ReasoningResult] = None
    raw_question: str = ""
    errors: List[str] = Field(default_factory=list)

    def is_sufficient(self, threshold: float = 0.75) -> bool:
        """Returns True when context quality meets the threshold."""
        return self.quality.score >= threshold

    def has_errors(self) -> bool:
        return len(self.errors) > 0
