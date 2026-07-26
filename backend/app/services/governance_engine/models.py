from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class GovernanceFinding(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    resource_ids: List[str]

class GovernanceRule(BaseModel):
    id: str
    name: str
    description: str

class GovernancePolicy(BaseModel):
    id: str
    name: str
    scope: str
    rules: List[GovernanceRule]

class GovernanceViolation(BaseModel):
    id: str
    policy_id: str
    rule_id: str
    description: str
    resource_ids: List[str]
    severity: str

class GovernanceRecommendation(BaseModel):
    id: str
    title: str
    description: str
    impact: str
    effort: str
    resource_ids: List[str]

class GovernanceRisk(BaseModel):
    overall_risk: str
    compliance_risk: str
    security_risk: str
    financial_risk: str

class GovernanceScore(BaseModel):
    overall_score: float
    category_scores: Dict[str, float]

class OwnershipAssessment(BaseModel):
    status: str
    missing_business_owners: List[str]
    missing_technical_owners: List[str]
    missing_application_owners: List[str]
    findings: List[GovernanceFinding]

class TagCompliance(BaseModel):
    status: str
    missing_required_tags: Dict[str, List[str]]
    invalid_tags: Dict[str, List[str]]
    findings: List[GovernanceFinding]

class NamingConventionAssessment(BaseModel):
    status: str
    duplicate_names: List[str]
    invalid_names: List[str]
    reserved_prefix_violations: List[str]
    findings: List[GovernanceFinding]

class BudgetGovernance(BaseModel):
    status: str
    unallocated_spend: float
    missing_cost_centers: List[str]
    findings: List[GovernanceFinding]

class LifecycleAssessment(BaseModel):
    status: str
    orphan_resources: List[str]
    end_of_life_resources: List[str]
    deprecated_resources: List[str]
    findings: List[GovernanceFinding]

class AccessGovernance(BaseModel):
    status: str
    unused_roles: List[str]
    expired_access: List[str]
    shared_credentials: List[str]
    findings: List[GovernanceFinding]

class GovernanceProfile(BaseModel):
    id: str
    target_id: str
    policies: List[GovernancePolicy] = []

class GovernanceAssessment(BaseModel):
    id: str
    target_id: str
    ownership: OwnershipAssessment
    tags: TagCompliance
    naming: NamingConventionAssessment
    access: AccessGovernance
    cost: BudgetGovernance
    lifecycle: LifecycleAssessment
    violations: List[GovernanceViolation]
    recommendations: List[GovernanceRecommendation]
    risk: GovernanceRisk
    score: GovernanceScore
    executive_summary: str = ""
    governance_summary: str = ""
    ownership_summary: str = ""
    policy_summary: str = ""
    tag_summary: str = ""
    budget_summary: str = ""
    risk_summary: str = ""
    business_impact: str = ""
    ai_explanation: str = ""

class GovernanceReport(BaseModel):
    coverage_report: str
    readiness_report: str
    technical_debt_report: str
    known_limitations: List[str]
    implementation_status: str
