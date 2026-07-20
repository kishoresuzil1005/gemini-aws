from app.services.ai.assistant.workflow.workflow_models import WorkflowStatus, WorkflowPlan

class InvalidWorkflowTransitionError(Exception):
    pass

class WorkflowStateMachine:
    """Controls valid lifecycle transitions for workflows."""
    
    VALID_TRANSITIONS = {
        WorkflowStatus.PENDING: [WorkflowStatus.VALIDATING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
        WorkflowStatus.VALIDATING: [WorkflowStatus.VALIDATED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
        WorkflowStatus.VALIDATED: [WorkflowStatus.SCHEDULING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
        WorkflowStatus.SCHEDULING: [WorkflowStatus.SCHEDULED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
        WorkflowStatus.SCHEDULED: [WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
        WorkflowStatus.RUNNING: [WorkflowStatus.SUSPENDED, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.COMPENSATING, WorkflowStatus.CANCELLED],
        WorkflowStatus.SUSPENDED: [WorkflowStatus.RESUMED, WorkflowStatus.CANCELLED],
        WorkflowStatus.RESUMED: [WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
        WorkflowStatus.COMPLETED: [],
        WorkflowStatus.FAILED: [WorkflowStatus.COMPENSATING],
        WorkflowStatus.COMPENSATING: [WorkflowStatus.ROLLED_BACK, WorkflowStatus.FAILED],
        WorkflowStatus.ROLLED_BACK: [],
        WorkflowStatus.CANCELLED: []
    }

    def transition(self, plan: WorkflowPlan, new_status: WorkflowStatus) -> bool:
        current_status = plan.status
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        
        if new_status not in allowed:
            raise InvalidWorkflowTransitionError(
                f"Illegal workflow transition: Cannot move from {current_status} to {new_status}"
            )
            
        plan.status = new_status
        return True