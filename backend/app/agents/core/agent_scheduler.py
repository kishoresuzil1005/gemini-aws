from typing import Dict, Any, List
from .agent_manager import AgentManager
from ..base.base_task import SubTask, TaskStatus

class AgentScheduler:
    def __init__(self, manager: AgentManager):
        self.manager = manager
        
    def schedule_task(self, subtask: SubTask, domain: str) -> bool:
        agents = self.manager.get_available_agents_for_domain(domain)
        if not agents:
            return False
            
        # Very simple scheduling: pick the first one
        best_agent = agents[0]
        subtask.assigned_agent_id = best_agent.agent_id
        subtask.status = TaskStatus.QUEUED
        
        # Here we would actually dispatch the task to the agent's queue
        return True
