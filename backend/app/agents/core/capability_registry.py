from typing import Dict, List, Optional
from ..base.base_agent import AgentCapability

class CapabilityRegistry:
    """
    Maintains a mapping of specific capabilities to the agents that can perform them.
    Allows dynamic discovery without hardcoding domain assignments.
    """
    def __init__(self):
        self._capabilities: Dict[str, List[str]] = {}  # capability_name -> List of agent_ids
        self._capability_details: Dict[str, AgentCapability] = {}

    def register_capability(self, agent_id: str, capability: AgentCapability):
        if capability.capability_name not in self._capabilities:
            self._capabilities[capability.capability_name] = []
        if agent_id not in self._capabilities[capability.capability_name]:
            self._capabilities[capability.capability_name].append(agent_id)
        self._capability_details[capability.capability_name] = capability

    def find_agents_by_capability(self, capability_name: str) -> List[str]:
        return self._capabilities.get(capability_name, [])

    def get_capability_details(self, capability_name: str) -> Optional[AgentCapability]:
        return self._capability_details.get(capability_name)
