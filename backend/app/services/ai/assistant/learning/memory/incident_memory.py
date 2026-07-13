from typing import List
from app.services.ai.assistant.learning.models.learning_models import IncidentPattern

class IncidentMemory:
    """Stores known incident patterns and what remediations worked best."""
    
    def __init__(self):
        self._incidents: List[IncidentPattern] = []
        
    def recognize_incident(self, signature: str) -> IncidentPattern:
        for i in self._incidents:
            if i.incident_signature == signature:
                return i
        return None
        
    def store_incident(self, pattern: IncidentPattern):
        self._incidents.append(pattern)