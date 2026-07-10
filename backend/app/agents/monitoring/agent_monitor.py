from typing import Dict, Any
from ..core.agent_registry import AgentRegistry
import time

class AgentMonitor:
    """
    Monitors the health, state, and activity of all registered agents.
    """
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def check_health(self) -> Dict[str, Any]:
        """
        Verify all agents are responsive (mock implementation).
        """
        now = time.time()
        health_report = {}
        for agent_id, agent in self.registry._agents.items():
            state = self.registry.get_state(agent_id)
            if state:
                time_since_heartbeat = (now - state.last_heartbeat.timestamp())
                is_healthy = time_since_heartbeat < 60  # 60 seconds threshold
                health_report[agent_id] = {
                    "status": "HEALTHY" if is_healthy else "UNRESPONSIVE",
                    "current_state": state.status,
                    "last_heartbeat": state.last_heartbeat.isoformat()
                }
        return health_report
