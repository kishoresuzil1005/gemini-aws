from app.services.ai.assistant.actions.action_models import ActionStatus, ActionPlan

class InvalidStateTransitionError(Exception):
    pass

class ActionStateMachine:
    """Controls valid action lifecycle transitions."""
    
    VALID_TRANSITIONS = {
        ActionStatus.PENDING: [ActionStatus.VALIDATED, ActionStatus.FAILED, ActionStatus.CANCELLED],
        ActionStatus.VALIDATED: [ActionStatus.APPROVAL_REQUIRED, ActionStatus.APPROVED, ActionStatus.REJECTED, ActionStatus.FAILED, ActionStatus.CANCELLED],
        ActionStatus.APPROVAL_REQUIRED: [ActionStatus.APPROVED, ActionStatus.REJECTED, ActionStatus.CANCELLED],
        ActionStatus.APPROVED: [ActionStatus.DRY_RUN_COMPLETE, ActionStatus.FAILED, ActionStatus.CANCELLED],
        ActionStatus.DRY_RUN_COMPLETE: [ActionStatus.EXECUTING, ActionStatus.CANCELLED, ActionStatus.FAILED],
        ActionStatus.EXECUTING: [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.CANCELLED],
        ActionStatus.COMPLETED: [ActionStatus.ROLLED_BACK],
        ActionStatus.FAILED: [],
        ActionStatus.REJECTED: [],
        ActionStatus.ROLLED_BACK: [],
        ActionStatus.CANCELLED: []
    }

    def transition(self, plan: ActionPlan, new_status: ActionStatus) -> bool:
        """
        Attempts to transition the plan to the new status.
        Raises InvalidStateTransitionError if the transition is illegal.
        """
        current_status = plan.status
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        
        if new_status not in allowed:
            raise InvalidStateTransitionError(
                f"Illegal transition: Cannot move from {current_status} to {new_status}"
            )
            
        plan.status = new_status
        return Tru