from typing import List, Dict, Any
from ..core.agent_manager import AgentManager
from .director_policy import DirectorPolicy

class DirectorEngine:
    """
    The 'CEO' of the Multi-Agent layer. Decides which agents are needed,
    priorities, parallel execution, and resource allocation for a given workflow.
    """
    def __init__(self, manager: AgentManager, policy: DirectorPolicy):
        self.manager = manager
        self.policy = policy

    def allocate_agents(self, workflow_context: Dict[str, Any]) -> List[str]:
        # Based on policy, select a subset of available agents rather than all
        print("[DirectorEngine] Analyzing workflow to allocate necessary agents...")
        required_domains = self.policy.determine_required_domains(workflow_context)
        
        allocated_agents = []
        for domain in required_domains:
            agents = self.manager.get_available_agents_for_domain(domain)
            if agents:
                allocated_agents.append(agents[0].agent_id)
                
        return allocated_agents
