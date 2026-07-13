from typing import List, Optional
from app.services.ai.assistant.memory.memory_store import MemoryStore
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, WorkflowStatus

class WorkflowRepository:
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store
        
    def save_workflow(self, plan: WorkflowPlan):
        """
        Saves the workflow metadata to persistence.
        """
        self.store.add_memory(
            session_id="system_workflows",
            role="system",
            content=f"WORKFLOW_METADATA: {plan.workflow_id}",
            metadata=plan.model_dump(mode='json')
        )

    def load_workflow(self, workflow_id: str) -> Optional[WorkflowPlan]:
        """
        Loads the workflow metadata from persistence.
        """
        history = self.store.get_history("system_workflows")
        for m in reversed(history):
            if m.content == f"WORKFLOW_METADATA: {workflow_id}" and m.metadata:
                return WorkflowPlan(**m.metadata)
        return None

    def list_workflows_by_status(self, status: WorkflowStatus) -> List[WorkflowPlan]:
        """
        Lists all workflows matching a specific status.
        """
        history = self.store.get_history("system_workflows")
        workflows = []
        seen = set()
        for m in reversed(history):
            if m.content.startswith("WORKFLOW_METADATA:"):
                wf_id = m.content.split(": ")[1]
                if wf_id not in seen and m.metadata:
                    seen.add(wf_id)
                    plan = WorkflowPlan(**m.metadata)
                    if plan.status == status:
                        workflows.append(plan)
        return workflow