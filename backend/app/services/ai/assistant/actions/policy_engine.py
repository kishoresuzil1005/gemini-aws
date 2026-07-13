from typing import Tuple, List
from app.services.ai.assistant.actions.action_models import ActionPlan, ActionStatus
from app.services.ai.assistant.actions.action_rules import ACTION_POLICIES
from app.services.ai.assistant.actions.action_state_machine import ActionStateMachine

class PolicyEngine:
    def __init__(self, state_machine: ActionStateMachine):
        self.state_machine = state_machine

    def check_policies(self, plan: ActionPlan) -> Tuple[bool, List[str]]:
        """
        Enforces organization-wide governance.
        E.g., "No DELETES in PROD", "No modification without Budget Approval".
        """
        errors = []
        action_name = plan.request.action_name
        
        policy = ACTION_POLICIES.get(action_name)
        if policy:
            # Check production rules
            is_prod = plan.request.context.region == "us-east-1" # Simulated PROD check
            if is_prod and not policy.get("allowed_in_production", True):
                errors.append(f"Action '{action_name}' is expressly forbidden in Production environments.")
                
        if errors:
            self.state_machine.transition(plan, ActionStatus.REJECTED)
            return False, errors
            
        return True, []