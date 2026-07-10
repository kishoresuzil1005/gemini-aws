from typing import List, Dict, Optional
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class LearningRepository:
    """Abstract storage interface for Decision Memory (Stage 1: In-Memory, Stage 2: SQLite)."""
    
    def __init__(self):
        # Stage 1: In-Memory Mock
        self._outcomes: List[ExecutionOutcome] = []
        
    def save_outcome(self, outcome: ExecutionOutcome):
        self._outcomes.append(outcome)
        
    def get_outcomes_for_action(self, action: str) -> List[ExecutionOutcome]:
        return [o for o in self._outcomes if o.action == action]
        
    def clear(self):
        self._outcomes = []
