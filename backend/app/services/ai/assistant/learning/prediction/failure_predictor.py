from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class FailurePredictor:
    """Predicts likelihood of failure based on past failures of similar actions."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def predict_failure_probability(self, action: str) -> float:
        history = self.memory.recall_action(action)
        if not history:
            return 50.0
            
        failures = sum(1 for h in history if h.status == "FAILURE")
        return (failures / len(history)) * 100.