from typing import Callable
from app.services.ai.assistant.workflow.workflow_models import WorkflowRequest, WorkflowPlan, WorkflowStatus
from app.services.ai.assistant.workflow.workflow_state_machine import WorkflowStateMachine
from app.services.ai.assistant.workflow.workflow_planner import WorkflowPlanner
from app.services.ai.assistant.workflow.workflow_validator import WorkflowValidator
from app.services.ai.assistant.workflow.workflow_scheduler import WorkflowScheduler
from app.services.ai.assistant.workflow.workflow_executor import WorkflowExecutor
from app.services.ai.assistant.workflow.workflow_checkpoint import WorkflowCheckpoint
from app.services.ai.assistant.workflow.workflow_retry_engine import WorkflowRetryEngine
from app.services.ai.assistant.workflow.workflow_compensation import WorkflowCompensation
from app.services.ai.assistant.workflow.workflow_monitor import WorkflowMonitor
from app.services.ai.assistant.actions.action_models import ActionResult

class WorkflowEngine:
    def __init__(self, checkpoint_store):
        self.state_machine = WorkflowStateMachine()
        self.planner = WorkflowPlanner()
        self.validator = WorkflowValidator(self.state_machine)
        self.scheduler = WorkflowScheduler(self.state_machine)
        
        self.checkpoint = WorkflowCheckpoint(checkpoint_store)
        self.retry_engine = WorkflowRetryEngine()
        self.compensation = WorkflowCompensation(self.state_machine)
        self.monitor = WorkflowMonitor()
        
        self.executor = WorkflowExecutor(self.state_machine, self.retry_engine, self.checkpoint, self.monitor)

    def process_workflow(self, request: WorkflowRequest, action_runner: Callable) -> WorkflowPlan:
        """
        The master conductor for Phase 6.
        Orchestrates the planner, validator, scheduler, executor, and compensation.
        The `action_runner` is a callback to Phase 5's action pipeline for individual steps.
        """
        # 1. Plan
        plan = self.planner.plan_workflow(request)
        
        # 2. Validate
        is_valid, errors = self.validator.validate(plan)
        if not is_valid:
            plan.error = "; ".join(errors)
            return plan
            
        # 3. Schedule
        try:
            stages = self.scheduler.schedule(plan)
        except Exception as e:
            plan.error = str(e)
            return plan
            
        # 4. Execute
        success = self.executor.execute(plan, stages, action_runner)
        
        # 5. Compensate (if failed)
        if not success:
            self.monitor.track_workflow(plan)
            comp_plan = self.compensation.create_compensation_plan(plan)
            # In a full system, we would then execute the comp_plan using the same executor logic
            
        return plan