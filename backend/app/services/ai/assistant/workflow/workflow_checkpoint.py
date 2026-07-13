from typing import List, Optional
from app.services.ai.assistant.memory.memory_store import MemoryStore
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, CheckpointRecord, WorkflowStatus

class WorkflowCheckpoint:
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store
        
    def save_checkpoint(self, plan: WorkflowPlan, step_id: str):
        """
        Saves the precise execution state.
        Uses MemoryStore for now, simulating cross-process persistence.
        """
        completed = [s.step_id for s in plan.steps if s.status == WorkflowStatus.COMPLETED]
        record = CheckpointRecord(
            workflow_id=plan.workflow_id,
            step_id=step_id,
            completed_steps=completed,
            variables={},
            temporary_outputs={}
        )
        self.store.add_memory(
            session_id=plan.workflow_id,
            role="system",
            content=f"CHECKPOINT: {step_id}",
            metadata=record.model_dump(mode='json')
        )

    def load_last_checkpoint(self, workflow_id: str) -> Optional[CheckpointRecord]:
        """
        Retrieves the last saved checkpoint for a workflow.
        """
        history = self.store.get_history(workflow_id)
        checkpoints = [m for m in history if m.content.startswith("CHECKPOINT")]
        if not checkpoints:
            return None
            
        last = checkpoints[-1]
        if last.metadata:
            return CheckpointRecord(**last.metadata)
        return Non