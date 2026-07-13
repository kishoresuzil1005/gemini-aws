from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ActionStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    DRY_RUN_COMPLETE = "DRY_RUN_COMPLETE"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class ActionContext(BaseModel):
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    cloud_account: Optional[str] = None
    region: Optional[str] = None
    provider_name: str
    approval_id: Optional[str] = None
    execution_id: str
    correlation_id: str
    request_id: str

class ActionRequest(BaseModel):
    action_name: str
    resource_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: ActionContext

class DryRunResult(BaseModel):
    estimated_downtime_minutes: int = 0
    estimated_cost_change: float = 0.0
    affected_resources: List[str] = Field(default_factory=list)
    risk_level: str = "INFO"
    warnings: List[str] = Field(default_factory=list)
    rollback_available: bool = False
    summary: str

class ExecutionResult(BaseModel):
    provider_status: str
    latency_ms: int
    raw_response: Dict[str, Any]
    error: Optional[str] = None

class RollbackPlan(BaseModel):
    rollback_available: bool
    snapshot_ids: List[str] = Field(default_factory=list)
    rollback_commands: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)

class AuditRecord(BaseModel):
    who: str
    when: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    why: str
    action: str
    resource: str
    approval_proof: Optional[str] = None
    execution_proof: Optional[str] = None
    rollback_plan: Optional[RollbackPlan] = None
    status: str

class ExecutionLog(BaseModel):
    action: str
    resource: str
    execution_time_ms: int
    result: str
    errors: List[str] = Field(default_factory=list)
    retries: int = 0
    provider: str

class ActionResult(BaseModel):
    status: ActionStatus
    action_completed: bool = False
    rollback_created: bool = False
    audit_logged: bool = False
    user_message: str
    execution_result: Optional[ExecutionResult] = None
    dry_run: Optional[DryRunResult] = None

class ActionStep(BaseModel):
    step_name: str
    status: ActionStatus = ActionStatus.PENDING
    details: Optional[Dict[str, Any]] = None

class ActionPlan(BaseModel):
    plan_id: str
    request: ActionRequest
    status: ActionStatus = ActionStatus.PENDING
    steps: List[ActionStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApprovalRequest(BaseModel):
    plan_id: str
    action_name: str
    resource_id: str
    reason: str
    dry_run_summary: str
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApprovalResult(BaseModel):
    approved: bool
    approver: str
    reason: str
    approved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))