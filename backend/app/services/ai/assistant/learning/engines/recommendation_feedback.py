from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class RecommendationFeedbackEngine:
    """Learns whether the user actually accepted or ignored the AI's recommendation."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def process_user_feedback(self, action: str, accepted: bool):
        # Record a synthetic outcome to represent user preference
        outcome = ExecutionOutcome(
            workflow_id="manual",
            action=action,
            status="SUCCESS" if accepted else "FAILURE",
            latency_ms=0,
            user_accepted=accepted
        )
        self.memory.remember(outcome