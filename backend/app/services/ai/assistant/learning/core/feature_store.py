from typing import Dict, Any, List
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class FeatureStore:
    """Converts raw execution history into reusable machine learning features."""
    
    def extract_features(self, outcome: ExecutionOutcome) -> List[float]:
        """
        Example feature vector generation:
        [is_success(1/0), latency, cost, was_accepted(1/0)]
        """
        vector = [
            1.0 if outcome.status == "SUCCESS" else 0.0,
            float(outcome.latency_ms),
            outcome.cost_impact or 0.0,
            1.0 if outcome.user_accepted else 0.0
        ]
        return vector
