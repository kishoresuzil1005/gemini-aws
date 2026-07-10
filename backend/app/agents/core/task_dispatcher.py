from typing import List
from ..base.base_task import AgentTask, SubTask, TaskStatus
from .agent_scheduler import AgentScheduler

class TaskDispatcher:
    def __init__(self, scheduler: AgentScheduler):
        self.scheduler = scheduler

    def dispatch(self, task: AgentTask):
        """Dispatch subtasks to appropriate agents"""
        for subtask in task.subtasks:
            if subtask.status == TaskStatus.PENDING:
                # We determine domain from metadata or description (mocking here)
                domain = self._infer_domain_from_subtask(subtask)
                success = self.scheduler.schedule_task(subtask, domain)
                if not success:
                    subtask.status = TaskStatus.FAILED

    def _infer_domain_from_subtask(self, subtask: SubTask) -> str:
        # Simple heuristic mapping for the mock
        desc = subtask.description.lower()
        if "network" in desc or "vpc" in desc: return "networking"
        if "security" in desc or "iam" in desc: return "security"
        if "database" in desc or "sql" in desc: return "database"
        if "kubernetes" in desc or "pod" in desc: return "kubernetes"
        if "cost" in desc or "budget" in desc: return "finops"
        if "monitor" in desc or "alert" in desc: return "sre"
        return "infrastructure"
