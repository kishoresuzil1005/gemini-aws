from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class AuditRecord(BaseModel):
    timestamp: datetime
    prediction: float
    confidence: float
    outcome: str
    model_version: str
    features: List[float]

class LearningAudit:
    """Tracks historical predictions vs actual outcomes for model debugging and audit dashboards."""
    
    def __init__(self):
        self.records: List[AuditRecord] = []
        
    def log_audit(self, prediction: float, confidence: float, outcome: str, features: List[float], model_version: str):
        self.records.append(AuditRecord(
            timestamp=utc_now(),
            prediction=prediction,
            confidence=confidence,
            outcome=outcome,
            model_version=model_version,
            features=features
        )