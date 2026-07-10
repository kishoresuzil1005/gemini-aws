from typing import Dict, List, Optional
from ..base.base_agent import AgentConfig, AgentState

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentConfig] = {}
        self._states: Dict[str, AgentState] = {}

    def add_agent(self, agent: AgentConfig):
        self._agents[agent.agent_id] = agent
        self._states[agent.agent_id] = AgentState(agent_id=agent.agent_id)

    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        return self._agents.get(agent_id)

    def get_agents_by_domain(self, domain: str) -> List[AgentConfig]:
        return [a for a in self._agents.values() if a.domain == domain and a.is_active]

    def update_state(self, agent_id: str, state: AgentState):
        if agent_id in self._agents:
            self._states[agent_id] = state

    def get_state(self, agent_id: str) -> Optional[AgentState]:
        return self._states.get(agent_id)
