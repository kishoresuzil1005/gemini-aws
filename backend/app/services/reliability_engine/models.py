from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AvailabilityAssessment(BaseModel):
    resource_id: str
    single_points_of_failure: int
    is_multi_az: bool
    is_multi_region: bool
    redundancy_level: str
    assessment: str

class FailureImpact(BaseModel):
    affected_components: List[str]
    business_impact: str
    severity: str

class FailureMode(BaseModel):
    component_type: str
    failure_type: str
    probability: str

class FailureScenario(BaseModel):
    scenario_id: str
    description: str
    mode: FailureMode
    impact: FailureImpact

class ResilienceProfile(BaseModel):
    resource_id: str
    fault_isolation: str
    auto_recovery_enabled: bool
    graceful_degradation_enabled: bool
    retry_strategy: str

class RecoveryStep(BaseModel):
    order: int
    action: str
    dependencies: List[str]

class RecoveryEstimate(BaseModel):
    estimated_time_mins: int
    complexity: str
    confidence: float

class RecoveryPlan(BaseModel):
    plan_id: str
    resource_id: str
    steps: List[RecoveryStep]
    estimate: RecoveryEstimate

class SLOAssessment(BaseModel):
    target_availability: float
    current_availability: float
    error_budget_remaining: float
    status: str

class SLAAssessment(BaseModel):
    breach_risk: str
    financial_impact_risk: str

class MTTRAssessment(BaseModel):
    estimated_mttr_mins: float
    confidence: float

class MTBFAssessment(BaseModel):
    estimated_mtbf_days: float
    stability_trend: str

class RedundancyAssessment(BaseModel):
    component: str
    is_redundant: bool
    recommendation: str

class ReliabilityRisk(BaseModel):
    risk_type: str
    severity: str
    description: str

class ReliabilityScore(BaseModel):
    overall_score: int
    availability_score: int
    recovery_score: int
    resilience_score: int

class BusinessContinuityProfile(BaseModel):
    critical_services: List[str]
    dr_readiness: str
    recovery_priority: str

class ReliabilityRecommendation(BaseModel):
    title: str
    description: str
    reason: str
    evidence: str
    dependencies: List[str]
    cost_impact: str
    security_impact: str
    performance_impact: str
    business_impact: str
    rollback_plan: str
    affected_resources: List[str]

class CrossEngineReliabilityFinding(BaseModel):
    source_engine: str
    description: str
    impact: str

class ReliabilityFinding(BaseModel):
    id: str
    title: str
    description: str
    resource_id: str
    finding_type: str
    recommendations: List[ReliabilityRecommendation]

class ReliabilityProfile(BaseModel):
    resource_id: str
    score: ReliabilityScore
    availability: AvailabilityAssessment
    failure_scenarios: List[FailureScenario]
    resilience: ResilienceProfile
    recovery_plan: RecoveryPlan
    slo: SLOAssessment
    sla: SLAAssessment
    mttr: MTTRAssessment
    mtbf: MTBFAssessment
    business_continuity: BusinessContinuityProfile
    risks: List[ReliabilityRisk]
    findings: List[ReliabilityFinding]
    recommendations: List[ReliabilityRecommendation]
    cross_engine_findings: List[CrossEngineReliabilityFinding] = Field(default_factory=list)
