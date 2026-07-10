from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.services.ai.assistant.actions.action_models import ActionRequest, ActionPlan

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    SCHEDULING = "SCHEDULING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    RESUMED = "RESUMED"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class WorkflowStep(BaseModel):
    step_id: str
    action_request: ActionRequest
    depends_on: List[str] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    action_plan: Optional[ActionPlan] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

class CompensationPlan(BaseModel):
    original_workflow_id: str
    compensation_steps: List[WorkflowStep] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING

class WorkflowPlan(BaseModel):
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None
    compensation_plan: Optional[CompensationPlan] = None

class WorkflowRequest(BaseModel):
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    target_resources: List[str] = Field(default_factory=list)
    correlation_id: str

class CheckpointRecord(BaseModel):
    workflow_id: str
    step_id: str
    completed_steps: List[str] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    temporary_outputs: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
