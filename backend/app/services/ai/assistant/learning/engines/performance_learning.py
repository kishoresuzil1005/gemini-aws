from app.services.ai.assistant.learning.memory.decision_memory import DecisionMemory

class PerformanceLearningEngine:
    """Learns the historical latency / performance characteristics of executions."""
    
    def __init__(self, memory: DecisionMemory):
        self.memory = memory
        
    def get_average_latency_ms(self, action: str) -> int:
        history = self.memory.recall_action(action)
        latencies = [h.latency_ms for h in history if h.latency_ms > 0]
        if not latencies:
            return 0
        return sum(latencies) // len(latencies)
