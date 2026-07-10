from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class LearningPolicyManager:
    """Controls what the AI is allowed to learn. Discards sandbox/testing environments to prevent pollution."""
    
    def __init__(self):
        self.blocked_environments = ["sandbox", "testing", "chaos", "demo", "lab"]
        
    def should_learn_from(self, outcome: ExecutionOutcome, environment: str) -> bool:
        if environment.lower() in self.blocked_environments:
            return False
        return True
