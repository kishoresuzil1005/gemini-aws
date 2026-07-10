from typing import Dict, Any
from ..base.base_task import AgentTask
from .agent_simulator import AgentSimulator

class WorkflowSimulator:
    """
    Simulates an entire multi-agent workflow to observe decisions and catch potential
    conflicts or errors before actual execution.
    """
    def __init__(self, agent_simulator: AgentSimulator):
        self.agent_simulator = agent_simulator

    def simulate_workflow(self, task: AgentTask) -> Dict[str, Any]:
        print(f"[WorkflowSimulator] Simulating workflow for '{task.title}'")
        simulation_results = {}
        
        for subtask in task.subtasks:
            if subtask.assigned_agent_id:
                result = self.agent_simulator.simulate(subtask.assigned_agent_id, subtask, task.context)
                simulation_results[subtask.subtask_id] = result
            else:
                simulation_results[subtask.subtask_id] = {"status": "error", "message": "No agent assigned"}
                
        all_success = all(r.get("status") == "success" for r in simulation_results.values())
        
        return {
            "workflow_status": "simulation_passed" if all_success else "simulation_failed",
            "details": simulation_results
        }
