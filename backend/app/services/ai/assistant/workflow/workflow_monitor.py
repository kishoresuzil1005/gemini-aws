import logging
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, WorkflowStatus, WorkflowStep

logger = logging.getLogger("WorkflowMonitor")

class WorkflowMonitor:
    def __init__(self):
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            logger.addHandler(ch)
            logger.setLevel(logging.INFO)

    def track_workflow(self, plan: WorkflowPlan):
        """Emits progress events for the overall workflow."""
        logger.info(f"[Workflow {plan.workflow_id}] Status: {plan.status.value}")
        
    def track_step(self, step: WorkflowStep):
        """Emits progress events for an individual step."""
        logger.info(f"  -> [Step {step.step_id}] Status: {step.status.value}"