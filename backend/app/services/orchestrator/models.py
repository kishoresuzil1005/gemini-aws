from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class EnterpriseRecommendation(BaseModel):
    title: str
    description: str
    evidence: str
    dependencies: List[str]
    business_impact: str
    cost_impact: str
    security_impact: str
    performance_impact: str
    reliability_impact: str
    implementation_complexity: str
    rollback_complexity: str
    confidence_score: float
    official_aws_references: List[str]

class RemediationPlan(BaseModel):
    steps: List[str]
    estimated_time: str
    risk_level: str

class RootCauseAnalysis(BaseModel):
    what_happened: str
    why_happened: str
    failed_dependency: str
    involved_resources: List[str]
    blast_radius: str
    business_impact: str
    security_impact: str
    cost_impact: str
    performance_impact: str
    reliability_impact: str

class UnifiedIntelligenceReport(BaseModel):
    incident_id: str
    executive_summary: str
    technical_summary: str
    root_cause: RootCauseAnalysis
    
    # Engine Outputs
    dependency_analysis: Dict[str, Any]
    security_analysis: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    reliability_analysis: Dict[str, Any]
    
    business_impact: str
    official_aws_guidance: List[str]
    
    enterprise_recommendations: List[EnterpriseRecommendation]
    remediation_plan: RemediationPlan
    
    risk_level: str
    confidence_score: float
    references: List[str]
