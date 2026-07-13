from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class PolicyLearningEngine:
    """Prevents polluting memory with sandbox, testing, or chaos engineering executions."""
    
    def should_learn(self, outcome: ExecutionOutcome, environment: str) -> bool:
        if environment.lower() in ["sandbox", "test", "chaos"]:
            return False
        return Tru