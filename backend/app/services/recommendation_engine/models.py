from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

class RecommendationContext(BaseModel):
    target_id: str
    objectives: List[str]
    constraints: List[str]

class RecommendationRequest(BaseModel):
    request_id: str
    target_id: str
    query: str
    context: RecommendationContext
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

class RecommendationPriority(BaseModel):
    level: str  # CRITICAL, HIGH, MEDIUM, LOW
    score: float
    factors: List[str]

class RecommendationEvidence(BaseModel):
    source: str
    data: Any
    references: List[str]

class RecommendationRisk(BaseModel):
    description: str
    severity: str
    mitigation: str

class RecommendationBenefit(BaseModel):
    category: str
    description: str
    estimated_value: str

class RecommendationTradeOff(BaseModel):
    advantages: List[str]
    disadvantages: List[str]
    business_benefits: List[RecommendationBenefit]
    business_risks: List[RecommendationRisk]
    security_tradeoffs: List[str]
    cost_tradeoffs: List[str]
    performance_tradeoffs: List[str]
    reliability_tradeoffs: List[str]
    operational_tradeoffs: List[str]

class RecommendationPlan(BaseModel):
    implementation_order: List[str]
    dependencies: List[str]
    estimated_duration: str
    prerequisites: List[str]
    rollback_strategy: str
    validation_steps: List[str]
    success_criteria: List[str]

class Recommendation(BaseModel):
    id: str
    title: str
    description: str
    category: str
    priority: RecommendationPriority
    confidence: float
    evidence: List[RecommendationEvidence]
    tradeoffs: RecommendationTradeOff
    plan: RecommendationPlan
    status: str # BEST, ALTERNATIVE, REJECTED
    explanation: str

class RecommendationGroup(BaseModel):
    group_id: str
    category: str
    recommendations: List[Recommendation]

class RecommendationSummary(BaseModel):
    executive_recommendation: str
    technical_recommendation: str
    business_recommendation: str
    immediate_actions: List[str]
    short_term_actions: List[str]
    long_term_actions: List[str]

class RecommendationComparison(BaseModel):
    comparison_id: str
    scenario_description: str
    option_a: Recommendation
    option_b: Recommendation
    winner: str
    reasoning: str

class OptimalRecommendationSet(BaseModel):
    set_id: str
    overall_score: float
    selected_recommendations: List[Recommendation]
    multi_objective_summary: str

class RecommendationEngineReport(BaseModel):
    coverage_report: str
    readiness_report: str
    technical_debt_report: str
    known_limitations: List[str]
    implementation_status: str
