import time
from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class ForgettingEngine:
    """Applies time-decay to historical memory so recent experience dominates."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def apply_decay(self):
        # E.g. prune records older than 1 year or apply weight reduction
        pas