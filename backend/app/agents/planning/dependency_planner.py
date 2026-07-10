from typing import List
from ..base.base_task import AgentTask, SubTask

class DependencyPlanner:
    """
    Evaluates a set of subtasks and establishes execution dependencies based on domain knowledge.
    """
    def establish_dependencies(self, task: AgentTask) -> AgentTask:
        """
        Mock implementation: sequential dependency for simplicity.
        Subtask N depends on Subtask N-1.
        """
        subtasks = task.subtasks
        for i in range(1, len(subtasks)):
            subtasks[i].dependencies.append(subtasks[i-1].subtask_id)
        
        return task
