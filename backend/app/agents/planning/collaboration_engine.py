from typing import List, Dict
from ..base.base_task import AgentTask
from .task_decomposer import TaskDecomposer
from .dependency_planner import DependencyPlanner

class CollaborationEngine:
    """
    Orchestrates the initial planning phase by utilizing the Decomposer and Dependency Planner,
    preparing the task to be dispatched across multiple specialized agents.
    """
    def __init__(self, decomposer: TaskDecomposer, dependency_planner: DependencyPlanner):
        self.decomposer = decomposer
        self.dependency_planner = dependency_planner

    def prepare_collaboration_plan(self, intent: str, context: Dict = None) -> AgentTask:
        task = self.decomposer.decompose(intent, context)
        task = self.dependency_planner.establish_dependencies(task)
        return task
