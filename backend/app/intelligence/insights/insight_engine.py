from pydantic import BaseModel
from typing import List, Dict, Any
from ..models.intelligence_models import BusinessRecommendation

class CloudInsight(BaseModel):
    insight_id: str
    title: str
    category: str  # COST, SECURITY, PERFORMANCE
    business_value: str
    risk: str
    savings_usd: float
    confidence_score: float
    recommendation: BusinessRecommendation

class InsightEngine:
    """
    Aggregates domain-specific recommendations into unified Cloud Insights.
    """
    def generate_unified_insights(self, cost_recs, sec_recs, perf_recs) -> List[CloudInsight]:
        print("[InsightEngine] Consolidating multi-domain recommendations into unified insights...")
        return []
