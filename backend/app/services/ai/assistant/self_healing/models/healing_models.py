from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Incident(BaseModel):
    incident_id: str
    source: str
    severity: str
    resource_id: str
    raw_payload: Dict[str, Any]

class RepairPlan(BaseModel):
    plan_id: str
    incident_id: str
    objectives: List[Dict[str, Any]]
    requires_approval: bool
    confidence: float

class HealingResult(BaseModel):
    incident_id: str
    success: bool
    rollback_triggered: bool
    duration_seconds: float