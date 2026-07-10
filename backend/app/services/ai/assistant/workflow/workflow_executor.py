from datetime import datetime, timezone
from typing import List, Callable
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, WorkflowStatus, WorkflowStep
from app.services.ai.assistant.workflow.workflow_state_machine import WorkflowStateMachine
from app.services.ai.assistant.workflow.workflow_retry_engine import WorkflowRetryEngine
from app.services.ai.assistant.workflow.workflow_checkpoint import WorkflowCheckpoint
from app.services.ai.assistant.workflow.workflow_monitor import WorkflowMonitor
from app.services.ai.assistant.actions.action_models import ActionResult

class WorkflowExecutor:
    def __init__(self, state_machine: WorkflowStateMachine, retry_engine: WorkflowRetryEngine, checkpoint: WorkflowCheckpoint, monitor: WorkflowMonitor):
        self.state_machine = state_machine
        self.retry_engine = retry_engine
        self.checkpoint = checkpoint
        self.monitor = monitor

    def execute(self, plan: WorkflowPlan, stages: List[List[WorkflowStep]], action_runner: Callable[[WorkflowStep], ActionResult]) -> bool:
        """
        Iterates through the scheduled DAG and executes steps using the action runner.
        """
        self.state_machine.transition(plan, WorkflowStatus.RUNNING)
        self.monitor.track_workflow(plan)
        
        for stage_idx, stage in enumerate(stages):
            # In a real system, steps in a stage could run in parallel (e.g. using asyncio.gather)
            for step in stage:
                if step.status == WorkflowStatus.COMPLETED:
                    continue # Skip if already completed (e.g. from checkpoint resume)
                    
                step.status = WorkflowStatus.RUNNING
                step.started_at = datetime.now(timezone.utc)
                self.monitor.track_step(step)
                
                def run_func(s: WorkflowStep) -> ActionResult:
                    res = action_runner(s)
                    if not res.action_completed:
                        raise Exception(f"Action failed: {res.user_message}")
                    return res
                
                try:
                    action_res = self.retry_engine.execute_with_retry(step, run_func)
                    step.status = WorkflowStatus.COMPLETED
                    step.output = action_res.model_dump(mode='json')
                except Exception as e:
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    self.monitor.track_step(step)
                    self.state_machine.transition(plan, WorkflowStatus.FAILED)
                    self.checkpoint.save_checkpoint(plan, step.step_id)
                    return False
                    
                step.finished_at = datetime.now(timezone.utc)
                self.monitor.track_step(step)
                self.checkpoint.save_checkpoint(plan, step.step_id)
                
        self.state_machine.transition(plan, WorkflowStatus.COMPLETED)
        self.monitor.track_workflow(plan)
        return True
