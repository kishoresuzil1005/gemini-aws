from typing import Tuple, List
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, WorkflowStatus
from app.services.ai.assistant.workflow.workflow_state_machine import WorkflowStateMachine

class WorkflowValidator:
    def __init__(self, state_machine: WorkflowStateMachine):
        self.state_machine = state_machine

    def validate(self, plan: WorkflowPlan) -> Tuple[bool, List[str]]:
        """
        Validates the workflow DAG for circular dependencies and missing steps.
        """
        self.state_machine.transition(plan, WorkflowStatus.VALIDATING)
        
        errors = []
        step_ids = {step.step_id for step in plan.steps}
        
        for step in plan.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.step_id}' depends on missing step '{dep}'.")
        
        # In a real system, we would also run a cycle detection algorithm here (DFS) to detect circular dependencies.
        # Simplified for now.
        
        if errors:
            self.state_machine.transition(plan, WorkflowStatus.FAILED)
            return False, errors
            
        self.state_machine.transition(plan, WorkflowStatus.VALIDATED)
        return True, []