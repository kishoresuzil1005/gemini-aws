from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class OptimizationOpportunity(BaseModel):
    category: str
    description: str
    difficulty: str

class SavingsPlanAnalysis(BaseModel):
    plan_type: str
    estimated_savings: float
    coverage: float

class ReservedInstanceAnalysis(BaseModel):
    instance_type: str
    recommended_count: int
    estimated_savings: float

class CostRisk(BaseModel):
    severity: str
    description: str

class WasteFinding(BaseModel):
    resource_id: str
    waste_type: str
    wasted_cost: float
    reason: str

class RightsizingRecommendation(BaseModel):
    current_size: str
    recommended_size: str
    savings: float
    reason: str

class IdleResource(BaseModel):
    resource_id: str
    type: str
    idle_days: int
    potential_savings: float

class CostTrend(BaseModel):
    direction: str
    percentage: float
    period: str

class CostForecast(BaseModel):
    expected_cost: float
    period: str
    variance: float

class CostAnomaly(BaseModel):
    resource_id: str
    spike_amount: float
    reason: str
    date_detected: datetime

class CostAttribution(BaseModel):
    team: str
    project: str
    environment: str
    business_unit: str

class CostBreakdown(BaseModel):
    compute: float
    storage: float
    network: float
    other: float
    total: float

class CostRecommendation(BaseModel):
    title: str
    description: str
    estimated_savings: float
    optimization_type: str
    effort: str
    affected_resources: List[str]

class CostFinding(BaseModel):
    id: str
    title: str
    description: str
    resource_id: str
    cost: float
    finding_type: str # 'WASTE', 'ANOMALY', 'RIGHTSIZE', 'IDLE'
    recommendations: List[CostRecommendation]

class BusinessCost(BaseModel):
    total_cost: float
    breakdown: CostBreakdown
    attribution: CostAttribution
    trends: CostTrend
    forecast: CostForecast

class BudgetImpact(BaseModel):
    budget_id: str
    limit: float
    current_spend: float
    forecasted_spend: float
    is_exceeded: bool
