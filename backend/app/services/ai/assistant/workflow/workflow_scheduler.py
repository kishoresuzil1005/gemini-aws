from typing import List
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, WorkflowStep, WorkflowStatus
from app.services.ai.assistant.workflow.workflow_state_machine import WorkflowStateMachine

class WorkflowScheduler:
    def __init__(self, state_machine: WorkflowStateMachine):
        self.state_machine = state_machine

    def schedule(self, plan: WorkflowPlan) -> List[List[WorkflowStep]]:
        """
        Calculates the optimal execution order of steps based on dependencies.
        Returns a list of 'stages', where each stage is a list of steps that can be run in parallel.
        """
        self.state_machine.transition(plan, WorkflowStatus.SCHEDULING)
        
        stages = []
        remaining = {step.step_id: step for step in plan.steps}
        completed_deps = set()
        
        while remaining:
            # Find all steps whose dependencies are met
            current_stage = []
            for step_id, step in list(remaining.items()):
                if all(dep in completed_deps for dep in step.depends_on):
                    current_stage.append(step)
                    
            if not current_stage:
                # If we have remaining steps but no dependencies met, there's a circular dependency
                # (which should have been caught in validation, but just in case)
                self.state_machine.transition(plan, WorkflowStatus.FAILED)
                raise Exception("Unresolvable dependencies in workflow DAG.")
                
            stages.append(current_stage)
            for step in current_stage:
                completed_deps.add(step.step_id)
                del remaining[step.step_id]
                
        self.state_machine.transition(plan, WorkflowStatus.SCHEDULED)
        return stage