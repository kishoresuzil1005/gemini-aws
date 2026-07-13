from typing import List
from app.services.ai.assistant.learning.models.learning_models import RecommendationScore

class RecommendationRanker:
    """Ranks recommendations by holistic effectiveness (Success rate, Speed, Low Risk)."""
    
    def rank(self, scores: List[RecommendationScore]) -> List[RecommendationScore]:
        # TBD: Weighting algorithms
        return sorted(scores, key=lambda s: s.success_rate, reverse=True