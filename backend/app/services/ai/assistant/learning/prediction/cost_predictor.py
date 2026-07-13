from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class CostPredictor:
    """Predicts financial impact based on past executions."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def predict_cost_impact(self, action: str) -> float:
        history = self.memory.recall_action(action)
        if not history:
            return 0.0
            
        costs = [h.cost_impact for h in history if h.cost_impact is not None]
        if not costs:
            return 0.0
        return sum(costs) / len(costs)