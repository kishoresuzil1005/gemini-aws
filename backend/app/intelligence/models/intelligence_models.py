from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class CloudMetric(BaseModel):
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = datetime.utcnow()

class BusinessRecommendation(BaseModel):
    recommendation_id: str
    title: str
    description: str
    business_value: str  # HIGH, MEDIUM, LOW
    risk_level: str  # HIGH, MEDIUM, LOW
    estimated_savings_usd: float
    confidence_score: float
    estimated_time_minutes: int
    rollback_complexity: str # EASY, MODERATE, HARD
    impacted_systems: List[str]

class ExecutiveSummary(BaseModel):
    summary_id: str
    automation_rate: float
    mission_success_rate: float
    cloud_health_score: float
    monthly_spend_usd: float
    security_score: float
    compliance_score: float
    total_savings_usd: float
    roi_percentage: float
    generated_at: datetime = datetime.utcnow()
