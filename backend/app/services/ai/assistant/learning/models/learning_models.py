from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class LearningRecord(BaseModel):
    record_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    context: Dict[str, Any] = {}

class ExecutionOutcome(BaseModel):
    workflow_id: str
    action: str
    status: str # SUCCESS, FAILURE, ROLLBACK
    latency_ms: int
    error_code: Optional[str] = None
    cost_impact: Optional[float] = None
    user_accepted: Optional[bool] = None

class RecommendationScore(BaseModel):
    action: str
    confidence_score: float
    success_rate: float
    average_recovery_time_ms: int
    predicted_failure_probability: float
    
class IncidentPattern(BaseModel):
    incident_signature: str
    occurrence_count: int
    best_remediation_action: str
    remediation_success_rate: floa