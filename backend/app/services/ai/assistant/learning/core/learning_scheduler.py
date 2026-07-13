from typing import List
from app.services.ai.assistant.learning.models.learning_models import ExecutionOutcome

class LearningScheduler:
    """Queues executions for batch learning rather than blocking the main workflow thread."""
    
    def __init__(self):
        self._queue: List[ExecutionOutcome] = []
        
    def enqueue(self, outcome: ExecutionOutcome):
        self._queue.append(outcome)
        
    def run_batch_learning(self):
        # Triggers offline processing of the queue
        pas