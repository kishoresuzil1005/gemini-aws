from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.services.dependency_engine.models import DependencyPath, DependencyNode

class ComplianceReference(BaseModel):
    framework: str
    control: str
    description: str

class SecurityRisk(BaseModel):
    likelihood: str
    impact: str
    exploitability: str
    business_criticality: str
    score: int
    severity: str
    confidence: float

class SecurityEvidence(BaseModel):
    source: str
    details: Dict[str, Any]

class SecurityRecommendation(BaseModel):
    reason: str
    evidence: str
    risk: SecurityRisk
    affected_resources: List[str]
    business_impact: str
    remediation_steps: List[str]
    priority: str
    estimated_effort: str

class SecurityControl(BaseModel):
    name: str
    status: str
    description: str

class SecurityViolation(BaseModel):
    rule: str
    description: str
    resources: List[str]
    evidence: SecurityEvidence

class ThreatActor(BaseModel):
    type: str
    origin: str
    intent: str

class ThreatScenario(BaseModel):
    actor: ThreatActor
    objective: str
    description: str

class PrivilegeEscalation(BaseModel):
    source_identity: str
    target_identity: str
    method: str
    path: DependencyPath

class LateralMovement(BaseModel):
    source_resource: str
    target_resource: str
    method: str
    path: DependencyPath

class DataExposure(BaseModel):
    resource_id: str
    data_type: str
    exposure_type: str
    severity: str

class AttackPath(BaseModel):
    path: DependencyPath
    scenario: ThreatScenario
    vulnerabilities: List[str]
    risk: SecurityRisk

class SecurityFinding(BaseModel):
    id: str
    title: str
    description: str
    resource_id: str
    finding_type: str  # e.g., 'IAM', 'NETWORK', 'DATA', 'EXPOSURE'
    risk: SecurityRisk
    recommendations: List[SecurityRecommendation]
    compliance: List[ComplianceReference] = Field(default_factory=list)

class SecurityIssue(BaseModel):
    issue_id: str
    findings: List[SecurityFinding]
    narrative: str

class SecurityPosture(BaseModel):
    overall_score: int
    issues: List[SecurityIssue]
    attack_paths: List[AttackPath]
