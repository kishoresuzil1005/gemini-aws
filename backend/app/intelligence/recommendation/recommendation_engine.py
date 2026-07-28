from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any, List
from ..models.intelligence_models import BusinessRecommendation
from .recommendation_ranker import RecommendationRanker

class RecommendationEngine:
    """
    Central hub for processing, ranking, and outputting all intelligent recommendations
    derived from Cost, Security, and Performance analysis.
    """
    def __init__(self, ranker: RecommendationRanker):
        self.ranker = ranker

    def process_recommendations(self, raw_recommendations: List[BusinessRecommendation]) -> List[BusinessRecommendation]:
        logger.debug("[RecommendationEngine] Evaluating and ranking cross-domain recommendations...")
        # Filters out low confidence recommendations and ranks them by business value and ROI
        valid_recs = [r for r in raw_recommendations if r.confidence_score > 80.0]
        return self.ranker.rank(valid_recs)
