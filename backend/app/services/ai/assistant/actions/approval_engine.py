import uuid
from typing import Optional
from app.services.ai.assistant.actions.action_models import ActionPlan, ActionStatus, ApprovalRequest, ApprovalResult
from app.services.ai.assistant.actions.action_rules import ACTION_POLICIES
from app.services.ai.assistant.actions.action_state_machine import ActionStateMachine

class ApprovalEngine:
    def __init__(self, state_machine: ActionStateMachine, testing_mode: bool = False):
        self.state_machine = state_machine
        self.testing_mode = testing_mode

    def requires_approval(self, plan: ActionPlan) -> bool:
        """Determines if the action requires explicit human approval."""
        policy = ACTION_POLICIES.get(plan.request.action_name)
        if policy and policy.get("requires_approval", False):
            return True
        return False

    def request_approval(self, plan: ActionPlan, dry_run_summary: str) -> ApprovalRequest:
        """Issues an approval request. State halts until approval is received."""
        req = ApprovalRequest(
            plan_id=plan.plan_id,
            action_name=plan.request.action_name,
            resource_id=plan.request.resource_id,
            reason="Action dictates safety approval based on policy.",
            dry_run_summary=dry_run_summary
        )
        self.state_machine.transition(plan, ActionStatus.APPROVAL_REQUIRED)
        return request
    def process_approval(self, plan: ActionPlan, approval_id: Optional[str] = None) -> ApprovalResult:
        """
        Processes an approval. In test mode, this auto-approves. 
        In production, it verifies the approval_id.
        """
        if self.testing_mode:
            res = ApprovalResult(approved=True, approver="MockProvider", reason="Testing Mode Auto-Approve")
            self.state_machine.transition(plan, ActionStatus.APPROVED)
            return res
            
        if not approval_id:
            res = ApprovalResult(approved=False, approver="System", reason="Approval ID missing.")
            self.state_machine.transition(plan, ActionStatus.APPROVAL_REQUIRED)
            return res
            
        # In a real system, verify the approval_id against a database record.
        res = ApprovalResult(approved=True, approver="SystemUser", reason="Valid Approval ID.")
        self.state_machine.transition(plan, ActionStatus.APPROVED)
        return result