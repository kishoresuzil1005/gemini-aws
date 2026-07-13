from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, CompensationPlan, WorkflowStatus
from app.services.ai.assistant.workflow.workflow_state_machine import WorkflowStateMachine
from app.services.ai.assistant.workflow.workflow_rules import WORKFLOW_POLICIES

class WorkflowCompensation:
    def __init__(self, state_machine: WorkflowStateMachine):
        self.state_machine = state_machine
        
    def create_compensation_plan(self, plan: WorkflowPlan) -> CompensationPlan:
        """
        Calculates the reverse-actions needed to rollback the workflow.
        """
        policy = WORKFLOW_POLICIES.get(plan.name, {})
        if not policy.get("requires_compensation_plan", False):
            return CompensationPlan(original_workflow_id=plan.workflow_id)
            
        self.state_machine.transition(plan, WorkflowStatus.COMPENSATING)
        
        # A real system would reverse the DAG. We simulate this by reversing completed steps.
        compensation_steps = []
        for step in reversed(plan.steps):
            if step.status == WorkflowStatus.COMPLETED:
                # Create a reverse step (e.g. STOP -> START)
                # This is highly simplified
                rev_step = step.model_copy(deep=True)
                rev_step.step_id = f"undo_{step.step_id}"
                rev_step.status = WorkflowStatus.PENDING
                rev_step.depends_on = []
                compensation_steps.append(rev_step)
                
        c_plan = CompensationPlan(
            original_workflow_id=plan.workflow_id,
            compensation_steps=compensation_steps
        )
        plan.compensation_plan = c_plan
        return c_pla