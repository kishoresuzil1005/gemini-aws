from typing import List, Dict
from app.services.ai.assistant.learning.core.learning_repository import LearningRepository
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class DecisionMemory:
    """Long-term memory module remembering every decision ever generated."""
    
    def __init__(self, repository: LearningRepository):
        self.repository = repository
        
    def recall_action(self, action: str) -> List[ExecutionOutcome]:
        return self.repository.get_outcomes_for_action(action)
        
    def remember(self, outcome: ExecutionOutcome):
        self.repository.save_outcome(outcome)