from typing import List
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome
from app.services.ai.assistant.learning.core.learning_repository import LearningRepository

class ExecutionHistory:
    """Specifically tracks the raw timeline of workflow executions."""
    
    def __init__(self, repository: LearningRepository):
        self.repository = repository
        
    def get_recent_executions(self, limit: int = 100) -> List[ExecutionOutcome]:
        return self.repository._outcomes[-limit:]