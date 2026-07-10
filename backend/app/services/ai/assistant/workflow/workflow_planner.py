import uuid
from typing import List, Dict, Any
from app.services.ai.assistant.actions.action_models import ActionRequest, ActionContext
from app.services.ai.assistant.workflow.workflow_models import WorkflowPlan, WorkflowRequest, WorkflowStep, WorkflowStatus

class WorkflowPlanner:
    def plan_workflow(self, request: WorkflowRequest) -> WorkflowPlan:
        """
        Translates a high-level operational goal into a DAG of sequential and parallel WorkflowSteps.
        """
        workflow_id = str(uuid.uuid4())
        steps = []
        
        # Example dynamic generation
        if request.name == "UPGRADE_EKS_CLUSTER":
            # Just a mock DAG to show dependency resolution
            steps.append(self._build_step("drain_nodes", "DRAIN_EKS_NODES", request, workflow_id, []))
            steps.append(self._build_step("backup", "BACKUP_EKS", request, workflow_id, []))
            steps.append(self._build_step("upgrade_cp", "UPGRADE_CONTROL_PLANE", request, workflow_id, ["backup"]))
            steps.append(self._build_step("upgrade_workers", "UPGRADE_WORKERS", request, workflow_id, ["drain_nodes", "upgrade_cp"]))
            steps.append(self._build_step("health_check", "HEALTH_CHECK_EKS", request, workflow_id, ["upgrade_workers"]))
        else:
            steps.append(self._build_step("default_step", request.name, request, workflow_id, []))

        return WorkflowPlan(
            workflow_id=workflow_id,
            name=request.name,
            description=f"Workflow for {request.name}",
            steps=steps
        )
        
    def _build_step(self, step_id: str, action_name: str, request: WorkflowRequest, workflow_id: str, depends_on: List[str]) -> WorkflowStep:
        ctx = ActionContext(
            user_id="system",
            provider_name="MOCK",
            execution_id=str(uuid.uuid4()),
            correlation_id=request.correlation_id,
            request_id=workflow_id
        )
        req = ActionRequest(
            action_name=action_name,
            resource_id=request.target_resources[0] if request.target_resources else "unknown",
            parameters=request.parameters,
            context=ctx
        )
        return WorkflowStep(
            step_id=step_id,
            action_request=req,
            depends_on=depends_on
        )
