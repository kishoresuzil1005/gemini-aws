from pydantic import BaseModel
from typing import List, Optional

class Recommendation(BaseModel):
    action: str
    confidence_score: float
    success_rate: float
    average_recovery_time_ms: int
    predicted_failure_probability: float
    features_used: List[float] = [