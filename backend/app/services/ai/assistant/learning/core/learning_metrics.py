from typing import Dict
from app.services.ai.assistant.learning.core.learning_repository import LearningRepository

class LearningMetrics:
    """Tracks how many outcomes the AI has learned from and the overall global success rate."""
    
    def __init__(self, repository: LearningRepository):
        self.repository = repository
        
    def get_global_metrics(self) -> Dict[str, float]:
        outcomes = self.repository._outcomes
        if not outcomes:
            return {"total_learned": 0, "global_success_rate": 0.0}
            
        successes = sum(1 for o in outcomes if o.status == "SUCCESS")
        return {
            "total_learned": len(outcomes),
            "global_success_rate": (successes / len(outcomes)) * 100
        