import uuid
from typing import Optional
from app.services.ai.assistant.reasoning.reasoning_models import ReasoningResult
from app.services.ai.assistant.actions.action_models import ActionPlan, ActionRequest, ActionStatus, ActionStep

class ActionPlanner:
    def plan_action(self, request: ActionRequest, reasoning_result: Optional[ReasoningResult] = None) -> ActionPlan:
        """
        Converts an ActionRequest (and prior reasoning) into a sequenced ActionPlan.
        """
        plan = ActionPlan(
            plan_id=str(uuid.uuid4()),
            request=request,
            status=ActionStatus.PENDING,
            steps=[
                ActionStep(step_name="Validate", status=ActionStatus.PENDING),
                ActionStep(step_name="PolicyCheck", status=ActionStatus.PENDING),
                ActionStep(step_name="DryRun", status=ActionStatus.PENDING),
                ActionStep(step_name="Approval", status=ActionStatus.PENDING),
                ActionStep(step_name="Execute", status=ActionStatus.PENDING),
                ActionStep(step_name="Verify", status=ActionStatus.PENDING),
                ActionStep(step_name="Audit", status=ActionStatus.PENDING)
            ]
        )
        return plan
