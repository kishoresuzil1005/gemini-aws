from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

class AIRequest(BaseModel):
    id: str
    target_id: str
    query: str
    context: Optional[str] = None
    previous_queries: List[str] = []
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

class AIContext(BaseModel):
    session_id: str
    history: List[Dict[str, Any]]
    active_target: str

class AIIntent(BaseModel):
    intent_type: str
    confidence: float
    required_engines: List[str]
    parameters: Dict[str, Any]

class ReasoningStep(BaseModel):
    step_id: str
    engine_name: str
    action: str
    status: str
    result: Optional[Dict[str, Any]] = None

class AIReasoningPlan(BaseModel):
    plan_id: str
    intent: AIIntent
    execution_order: List[str]
    steps: List[ReasoningStep]

class Evidence(BaseModel):
    source: str
    description: str
    data: Any
    references: List[str]

class Confidence(BaseModel):
    score: float
    factors: List[str]

class Conflict(BaseModel):
    conflict_id: str
    description: str
    conflicting_sources: List[str]
    resolution: str

class Decision(BaseModel):
    decision_id: str
    recommendation: str
    evidence_ids: List[str]
    confidence: Confidence

class ReasoningChain(BaseModel):
    chain_id: str
    plan: AIReasoningPlan
    evidence: List[Evidence]
    conflicts: List[Conflict]
    decisions: List[Decision]
    merged_findings: List[Any]

class ExecutiveSummary(BaseModel):
    status: str
    headline: str
    key_takeaway: str

class TechnicalSummary(BaseModel):
    root_cause: str
    affected_resources: List[str]
    blast_radius: str

class BusinessSummary(BaseModel):
    business_impact: str
    cost_impact: str
    security_impact: str
    performance_impact: str
    reliability_impact: str

class AIResponse(BaseModel):
    response_id: str
    request: AIRequest
    executive_summary: ExecutiveSummary
    technical_summary: TechnicalSummary
    business_summary: BusinessSummary
    reasoning_chain: ReasoningChain
    recommended_actions: List[str]
    official_references: List[str]
    unified_explanation: str

class AIOrchestratorReport(BaseModel):
    coverage_report: str
    readiness_report: str
    technical_debt_report: str
    known_limitations: List[str]
    implementation_status: str
