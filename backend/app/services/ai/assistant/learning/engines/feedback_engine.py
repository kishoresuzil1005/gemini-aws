from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class FeedbackEngine:
    """Consumes raw workflow outcomes and updates the learning memory."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def process_execution_result(self, outcome: ExecutionOutcome):
        # Validate and store
        if outcome.status in ["SUCCESS", "FAILURE", "ROLLBACK"]:
            self.memory.remember(outcome)