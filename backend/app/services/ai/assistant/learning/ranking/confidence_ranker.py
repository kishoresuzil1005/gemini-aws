from typing import List
from app.services.ai.assistant.learning.models.learning_models import RecommendationScore

class ConfidenceRanker:
    """Ranks recommendations explicitly by the AI's internal confidence level."""
    
    def rank(self, scores: List[RecommendationScore]) -> List[RecommendationScore]:
        return sorted(scores, key=lambda s: s.confidence_score, reverse=True)
