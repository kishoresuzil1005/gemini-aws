from app.services.ai.assistant.learning.prediction.success_predictor import SuccessPredictor
from app.services.ai.assistant.learning.prediction.failure_predictor import FailurePredictor
from app.services.ai.assistant.learning.models.learning_models import RecommendationScore

class RecommendationEngine:
    """Scores a recommendation based on learning predictors."""
    
    def __init__(self, success_predictor: SuccessPredictor, failure_predictor: FailurePredictor):
        self.success_predictor = success_predictor
        self.failure_predictor = failure_predictor
        
    def generate_recommendation(self, action: str) -> RecommendationScore:
        success = self.success_predictor.predict_success_rate(action)
        failure = self.failure_predictor.predict_failure_probability(action)
        
        # Simple confidence calculation
        confidence = success - failure
        if confidence < 0:
            confidence = 0.0
            
        return RecommendationScore(
            action=action,
            confidence_score=confidence,
            success_rate=success,
            average_recovery_time_ms=0, # delegated to performance engine normally
            predicted_failure_probability=failure
        )