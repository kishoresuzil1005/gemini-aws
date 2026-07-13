from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome
from typing import Dict, Any

class DecisionEvaluator:
    """Compares the predicted outcome (e.g. 95% success) vs reality (Failed) and calibrates prediction weights."""
    
    def evaluate(self, prediction: Dict[str, Any], reality: ExecutionOutcome):
        pas