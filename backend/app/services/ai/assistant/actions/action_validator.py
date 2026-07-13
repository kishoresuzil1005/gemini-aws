from typing import Tuple, List
from app.services.ai.assistant.actions.action_models import ActionPlan, ActionStatus
from app.services.ai.assistant.actions.action_state_machine import ActionStateMachine

class ActionValidator:
    def __init__(self, state_machine: ActionStateMachine):
        self.state_machine = state_machine

    def validate(self, plan: ActionPlan) -> Tuple[bool, List[str]]:
        """
        Safety checks to ensure the action is structurally sound and contextually permitted.
        Never executes AWS logic.
        """
        errors = []
        
        if not plan.request.resource_id:
            errors.append("Resource ID is missing.")
            
        if not plan.request.action_name:
            errors.append("Action Name is missing.")
            
        if not plan.request.context.provider_name:
            errors.append("Provider Name is missing.")
            
        if errors:
            self.state_machine.transition(plan, ActionStatus.FAILED)
            return False, errors
            
        return True, [