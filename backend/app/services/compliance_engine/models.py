from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ComplianceProfile(BaseModel):
    id: str
    name: str
    description: str

class ComplianceEvidence(BaseModel):
    id: str
    source_engine: str
    finding_id: str
    description: str
    resource_ids: List[str]

class ComplianceRecommendation(BaseModel):
    id: str
    priority: str
    business_impact: str
    estimated_effort: str
    rollback_plan: str
    dependencies: List[str]
    risk_reduction: str
    implementation_steps: List[str]

class ComplianceViolation(BaseModel):
    id: str
    title: str
    severity: str
    description: str
    resource_ids: List[str]
    evidence: List[ComplianceEvidence]
    recommendation: Optional[ComplianceRecommendation] = None

class ComplianceFinding(BaseModel):
    id: str
    title: str
    status: str
    resource_ids: List[str]
    evidence: List[ComplianceEvidence]

class ComplianceControl(BaseModel):
    id: str
    name: str
    description: str
    status: str
    violations: List[ComplianceViolation] = []
    findings: List[ComplianceFinding] = []

class ComplianceRequirement(BaseModel):
    id: str
    name: str
    description: str
    controls: List[ComplianceControl]

class CompliancePolicy(BaseModel):
    id: str
    name: str
    requirements: List[ComplianceRequirement]

class ComplianceFramework(BaseModel):
    id: str
    name: str
    version: str
    policies: List[CompliancePolicy]

class ComplianceRisk(BaseModel):
    compliance_risk: str
    business_risk: str
    operational_risk: str
    security_risk: str
    regulatory_risk: str
    financial_risk: str
    overall_risk_level: str

class ComplianceScore(BaseModel):
    overall_score: float
    framework_scores: Dict[str, float]

class ComplianceGap(BaseModel):
    gap_type: str
    description: str
    severity: str
    affected_resources: List[str]

class ComplianceAssessment(BaseModel):
    id: str
    target_id: str
    frameworks: List[ComplianceFramework]
    score: ComplianceScore
    risk: ComplianceRisk
    gaps: List[ComplianceGap]
    executive_summary: str = ""
    compliance_summary: str = ""
    framework_summary: str = ""
    evidence_summary: str = ""
    violation_summary: str = ""
    business_impact: str = ""
    regulatory_impact: str = ""
    risk_narrative: str = ""
    remediation_narrative: str = ""
    ai_explanation: str = ""

class ComplianceReport(BaseModel):
    coverage_report: str
    known_limitations: List[str]
    technical_debt: List[str]
    implementation_status: str
