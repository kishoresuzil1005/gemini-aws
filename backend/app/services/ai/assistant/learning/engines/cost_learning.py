from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class CostLearningEngine:
    """Learns historical savings and expenditures from past actions."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def get_average_savings(self, action: str) -> float:
        history = self.memory.recall_action(action)
        savings = [h.cost_impact for h in history if h.cost_impact and h.cost_impact > 0]
        if not savings:
            return 0.0
        return sum(savings) / len(savings)