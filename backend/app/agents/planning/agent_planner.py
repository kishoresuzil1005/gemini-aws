from typing import List
from ..base.base_task import AgentTask, SubTask
from ..core.capability_registry import CapabilityRegistry

class AgentPlanner:
    """
    Intelligently selects the best agents for subtasks based on required capabilities
    rather than hardcoding domain assignments.
    """
    def __init__(self, capability_registry: CapabilityRegistry):
        self.capability_registry = capability_registry

    def assign_agents(self, task: AgentTask) -> AgentTask:
        for subtask in task.subtasks:
            # Simple keyword-to-capability matching for the mock
            capability_needed = self._infer_capability(subtask)
            candidates = self.capability_registry.find_agents_by_capability(capability_needed)
            
            if candidates:
                # Pick the first available candidate
                subtask.assigned_agent_id = candidates[0]
            else:
                print(f"[AgentPlanner] No agent found with capability: {capability_needed}")
                
        return task

    def _infer_capability(self, subtask: SubTask) -> str:
        desc = subtask.description.lower()
        if "secret" in desc or "iam" in desc: return "iam_management"
        if "network" in desc or "vpc" in desc: return "network_routing"
        if "kubernetes" in desc or "pod" in desc: return "k8s_orchestration"
        if "database" in desc or "sql" in desc: return "db_management"
        return "general_compute"
