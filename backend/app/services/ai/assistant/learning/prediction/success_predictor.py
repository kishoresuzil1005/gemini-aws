from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class SuccessPredictor:
    """Predicts probability of an action succeeding based on history."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def predict_success_rate(self, action: str) -> float:
        history = self.memory.recall_action(action)
        if not history:
            return 50.0 # Unknown
            
        successes = sum(1 for h in history if h.status == "SUCCESS")
        return (successes / len(history)) * 100.