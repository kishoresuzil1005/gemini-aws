from .agent_health_manager import AgentHealthManager
from .agent_registry import AgentRegistry

class AgentRecoveryManager:
    """
    Attempts to recover agents that are stuck or offline.
    """
    def __init__(self, health_manager: AgentHealthManager, registry: AgentRegistry):
        self.health_manager = health_manager
        self.registry = registry

    def attempt_recovery(self, agent_id: str) -> bool:
        health_status = self.health_manager.evaluate_health(agent_id)
        if health_status in ["STUCK", "OFFLINE"]:
            print(f"[RecoveryManager] Attempting to restart agent {agent_id}...")
            # In a real system, this would reload memory, reset state, and restart the process
            state = self.registry.get_state(agent_id)
            if state:
                state.status = "IDLE"
            print(f"[RecoveryManager] Agent {agent_id} restarted and state reset to IDLE.")
            return True
        return False
