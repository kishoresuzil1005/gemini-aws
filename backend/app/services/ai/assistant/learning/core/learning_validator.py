from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class LearningValidator:
    """Ensures learning data is valid and uncorrupted before saving to memory."""
    
    def validate_outcome(self, outcome: ExecutionOutcome) -> bool:
        if not outcome.action or not outcome.status:
            return False
        if outcome.status not in ["SUCCESS", "FAILURE", "ROLLBACK"]:
            return False
        return True