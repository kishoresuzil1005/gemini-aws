from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class RiskPredictor:
    """Estimates the risk (e.g. need for rollback) of executing an action."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def predict_rollback_risk(self, action: str) -> float:
        history = self.memory.recall_action(action)
        if not history:
            return 0.0
            
        rollbacks = sum(1 for h in history if h.status == "ROLLBACK")
        return (rollbacks / len(history)) * 100.0
