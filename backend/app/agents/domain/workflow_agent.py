from typing import Dict, Any
from ..base.base_task import AgentTask, SubTask
from ..base.base_agent import BaseAgent
from ..planning.collaboration_engine import CollaborationEngine
from ..coordination.consensus_engine import ConsensusEngine
from ..core.task_dispatcher import TaskDispatcher

class WorkflowAgent(BaseAgent):
    """
    Master Agent orchestrating and coordinating all other domain experts.
    """
    def __init__(self, agent_id: str, collaboration_engine: CollaborationEngine, consensus_engine: ConsensusEngine, dispatcher: TaskDispatcher):
        super().__init__(agent_id, "workflow")
        self.collaboration_engine = collaboration_engine
        self.consensus_engine = consensus_engine
        self.dispatcher = dispatcher

    def execute(self, task: SubTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        For WorkflowAgent, executing a task usually means coordinating a higher-level intent.
        Here we assume the SubTask description or name contains the intent.
        """
        intent = task.description
        print(f"[WorkflowAgent {self.agent_id}] Coordinating high-level intent: '{intent}'")
        
        # 1. Plan and Decompose
        plan = self.collaboration_engine.prepare_collaboration_plan(intent, context)
        
        # 2. Seek Consensus (if risky, skipping full impl details here for brevity)
        consensus = self.consensus_engine.reach_consensus("Execution of " + intent, [])
        if not consensus:
            print("[WorkflowAgent] Consensus failed. Aborting.")
            return {"status": "error", "message": "Consensus failed"}

        # 3. Dispatch to Sub-Agents
        self.dispatcher.dispatch(plan)
        
        return {"status": "success", "plan_id": plan.task_id}

    def coordinate_task(self, intent: str, context: Dict[str, Any] = None) -> AgentTask:
        # Legacy method for direct calling
        plan = self.collaboration_engine.prepare_collaboration_plan(intent, context)
        consensus = self.consensus_engine.reach_consensus("Execution of " + intent, [])
        if not consensus:
            return plan
        self.dispatcher.dispatch(plan)
        return plan
