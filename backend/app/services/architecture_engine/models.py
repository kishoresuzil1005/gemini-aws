from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ArchitectureProfile(BaseModel):
    id: str
    name: str
    description: str
    tier: str

class ArchitectureFinding(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    category: str
    resource_ids: List[str]

class ArchitectureRecommendation(BaseModel):
    id: str
    title: str
    description: str
    effort: str
    impact: str
    business_value: str

class ArchitectureRisk(BaseModel):
    id: str
    risk_type: str
    severity: str
    probability: str
    impact: str

class ArchitectureScore(BaseModel):
    overall_score: float
    category_scores: Dict[str, float]

class ArchitecturePattern(BaseModel):
    name: str
    detected_resources: List[str]
    confidence: float

class ArchitectureAntiPattern(BaseModel):
    name: str
    detected_resources: List[str]
    severity: str
    impact: str

class ArchitectureTopology(BaseModel):
    ingress_layers: List[str] = []
    load_balancers: List[str] = []
    api_gateways: List[str] = []
    compute_layers: List[str] = []
    containers: List[str] = []
    serverless: List[str] = []
    databases: List[str] = []
    messaging: List[str] = []
    caching: List[str] = []
    storage: List[str] = []
    networking: List[str] = []
    identity: List[str] = []
    observability: List[str] = []
    data_flow: Dict[str, Any] = {}
    dependency_flow: Dict[str, Any] = {}
    service_boundaries: List[str] = []

class ArchitectureTradeoff(BaseModel):
    dimension1: str
    dimension2: str
    analysis: str
    decision: str

class ArchitectureEvolution(BaseModel):
    current_state: str
    target_state: str
    steps: List[str]

class ModernizationRecommendation(BaseModel):
    source: str
    target: str
    reason: str
    effort: str

class ArchitectureModernizationPlan(BaseModel):
    recommendations: List[ModernizationRecommendation]
    estimated_effort_days: int

class WellArchitectedAssessment(BaseModel):
    operational_excellence: Dict[str, Any]
    security: Dict[str, Any]
    reliability: Dict[str, Any]
    performance_efficiency: Dict[str, Any]
    cost_optimization: Dict[str, Any]
    sustainability: Dict[str, Any]
    findings: List[ArchitectureFinding] = []

class ScalabilityAssessment(BaseModel):
    horizontal_scaling: Dict[str, Any]
    vertical_scaling: Dict[str, Any]
    elasticity: Dict[str, Any]
    capacity_growth: Dict[str, Any]
    traffic_distribution: Dict[str, Any]
    regional_expansion: Dict[str, Any]
    service_scaling: Dict[str, Any]
    data_scaling: Dict[str, Any]
    queue_scaling: Dict[str, Any]
    container_scaling: Dict[str, Any]

class ArchitectureDecision(BaseModel):
    recommended_architecture: str
    migration_path: str
    migration_complexity: str
    risk: str
    business_value: str
    technical_debt: str
    implementation_effort: str
    rollback_strategy: str

class ArchitectureAssessment(BaseModel):
    topology: ArchitectureTopology
    patterns: List[ArchitecturePattern]
    anti_patterns: List[ArchitectureAntiPattern]
    well_architected: WellArchitectedAssessment
    scalability: ScalabilityAssessment
    modernization: ArchitectureModernizationPlan
    tradeoffs: List[ArchitectureTradeoff]
    decision: ArchitectureDecision
    executive_summary: str = ""
    architecture_summary: str = ""
    architecture_narrative: str = ""
    strengths: List[str] = []
    weaknesses: List[str] = []
    technical_debt: List[str] = []
    modernization_opportunities: List[str] = []
    business_impact: str = ""
    migration_strategy: str = ""
    ai_explanation: str = ""

class ArchitectureImplementationReport(BaseModel):
    coverage_report: str
    readiness_report: str
    known_limitations: List[str]
    technical_debt: List[str]
    implementation_status: str
