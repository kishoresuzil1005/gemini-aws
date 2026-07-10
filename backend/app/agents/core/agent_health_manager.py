from typing import Dict, Any
from .agent_registry import AgentRegistry

class AgentHealthManager:
    """
    Dedicated manager to track agent lifecycle health: Healthy, Busy, Offline, Restarting, Stuck.
    """
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def evaluate_health(self, agent_id: str) -> str:
        state = self.registry.get_state(agent_id)
        if not state:
            return "UNKNOWN"
            
        if state.status == "OFFLINE":
            return "OFFLINE"
        elif state.status == "ERROR":
            return "STUCK"
        elif state.status == "WORKING":
            return "BUSY"
            
        return "HEALTHY"
        
    def check_all(self) -> Dict[str, str]:
        results = {}
        for agent_id in self.registry._agents:
            results[agent_id] = self.evaluate_health(agent_id)
        return results
