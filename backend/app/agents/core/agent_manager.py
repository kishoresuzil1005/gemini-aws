from typing import Dict, List, Optional
from ..base.base_agent import AgentConfig, AgentState
from .agent_registry import AgentRegistry

class AgentManager:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def register_agent(self, agent_config: AgentConfig):
        self.registry.add_agent(agent_config)

    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        return self.registry.get_agent(agent_id)

    def get_available_agents_for_domain(self, domain: str) -> List[AgentConfig]:
        return self.registry.get_agents_by_domain(domain)
        
    def update_agent_state(self, agent_id: str, state: AgentState):
        self.registry.update_state(agent_id, state)
