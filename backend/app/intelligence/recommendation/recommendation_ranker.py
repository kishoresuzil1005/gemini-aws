from typing import List
from ..models.intelligence_models import BusinessRecommendation

class RecommendationRanker:
    """
    Ranks recommendations based on ROI, Confidence, and Risk parameters.
    """
    def rank(self, recommendations: List[BusinessRecommendation]) -> List[BusinessRecommendation]:
        # Simple mock ranking: Prioritize CRITICAL/HIGH business value
        val_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return sorted(recommendations, key=lambda r: val_map.get(r.business_value, 0), reverse=True)
