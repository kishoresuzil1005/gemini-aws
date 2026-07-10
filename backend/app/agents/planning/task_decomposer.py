import uuid
from typing import List, Dict, Any
from ..base.base_task import AgentTask, SubTask, TaskStatus

class TaskDecomposer:
    """
    Takes a high-level goal and decomposes it into smaller actionable subtasks.
    In a real AI implementation, this relies on an LLM to generate the breakdown.
    """
    def decompose(self, intent: str, context: Dict[str, Any] = None) -> AgentTask:
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            title="Decomposed task for: " + intent[:30],
            intent=intent,
            context=context or {}
        )
        
        # Simplified deterministic mock for subtask generation based on intent keywords
        intent_lower = intent.lower()
        if "upgrade" in intent_lower and "kubernetes" in intent_lower:
            task.subtasks = [
                SubTask(
                    subtask_id=str(uuid.uuid4()),
                    name="Pre-upgrade Checks",
                    description="Run checks on infrastructure and cluster state.",
                    dependencies=[]
                ),
                SubTask(
                    subtask_id=str(uuid.uuid4()),
                    name="Backup State",
                    description="Backup etcd and cluster state.",
                    dependencies=[] # In real life, might depend on Pre-upgrade Checks
                ),
                SubTask(
                    subtask_id=str(uuid.uuid4()),
                    name="Perform Upgrade",
                    description="Upgrade control plane and nodes.",
                    dependencies=[] # Dependency planning done by DependencyPlanner
                )
            ]
        else:
            task.subtasks = [
                SubTask(
                    subtask_id=str(uuid.uuid4()),
                    name="General Execution",
                    description="Execute the requested action",
                    dependencies=[]
                )
            ]
            
        return task
