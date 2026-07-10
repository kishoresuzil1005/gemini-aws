from typing import List
from ..base.base_task import AgentTask

class PriorityScheduler:
    """
    Adjusts execution priorities of active tasks across the multi-agent system based on urgency.
    """
    def rank_tasks(self, active_tasks: List[AgentTask]) -> List[AgentTask]:
        """
        Sort tasks by priority descending.
        """
        return sorted(active_tasks, key=lambda t: t.priority, reverse=True)
