from app.services.ai.assistant.learning.memory.incident_memory import IncidentMemory

class IncidentLearningEngine:
    """Maps new incidents against historical data to find the best remediation."""
    
    def __init__(self, memory: IncidentMemory):
        self.memory = memory
        
    def suggest_remediation(self, signature: str) -> str:
        incident = self.memory.recognize_incident(signature)
        if incident and incident.remediation_success_rate > 0.8:
            return incident.best_remediation_action
        return "Requires new analysis"
