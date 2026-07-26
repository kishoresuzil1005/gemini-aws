from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

class ExecutionRequest(BaseModel):
    request_id: str
    target_id: str
    query: str
    automation_level: str # Observe Only, Recommend Only, Approval Required, Semi-Autonomous, Fully Autonomous
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

class SimulationResult(BaseModel):
    impact_estimate: str
    risk_estimate: str
    blast_radius: str
    downtime_estimate: str
    cost_estimate: str
    rollback_time_estimate: str
    safe_to_execute: bool

class SimulationReport(BaseModel):
    report_id: str
    results: SimulationResult

class ExecutionPolicy(BaseModel):
    policy_id: str
    description: str
    enforced: bool

class PolicyValidationReport(BaseModel):
    organization_policies_passed: bool
    business_policies_passed: bool
    security_policies_passed: bool
    compliance_policies_passed: bool
    maintenance_windows_passed: bool
    execution_windows_passed: bool
    approval_policies_passed: bool
    regional_policies_passed: bool
    overall_passed: bool

class ExecutionApproval(BaseModel):
    approval_type: str
    status: str
    approver: str
    timestamp: datetime.datetime

class ApprovalWorkflow(BaseModel):
    workflow_id: str
    required_approvals: List[str]
    approvals_collected: List[ExecutionApproval]
    is_approved: bool

class ExecutionStep(BaseModel):
    step_id: str
    action: str
    target: str
    status: str

class ExecutionStage(BaseModel):
    stage_id: str
    name: str
    steps: List[ExecutionStep]

class ExecutionWorkflow(BaseModel):
    workflow_id: str
    stages: List[ExecutionStage]
    execution_strategy: str # Dry Run, Canary, Blue/Green, Rolling, Phased

class ExecutionStatus(BaseModel):
    state: str # PENDING, SIMULATING, APPROVING, EXECUTING, SUCCESS, FAILED, ROLLING_BACK, ROLLED_BACK
    progress: float
    warnings: List[str]

class ExecutionResult(BaseModel):
    success: bool
    message: str
    output: Any

class RollbackExecution(BaseModel):
    rollback_id: str
    rollback_type: str # Automatic, Manual, Partial, Full
    status: ExecutionStatus
    validation_status: str

class ExecutionEvidence(BaseModel):
    source: str
    data: Any

class ExecutionAudit(BaseModel):
    audit_id: str
    initiator: str
    reason: str
    evidence: List[ExecutionEvidence]
    approval_chain: List[ExecutionApproval]
    policies_evaluated: PolicyValidationReport
    affected_resources: List[str]
    rollback_events: List[str]

class AuditReport(BaseModel):
    report_id: str
    audit_records: List[ExecutionAudit]

class ExecutionSummary(BaseModel):
    execution_id: str
    timeline: List[str]
    decisions: List[str]
    risk_summary: str
    business_summary: str
    rollback_summary: str
    validation_summary: str
    evidence_summary: str

class ExecutionPlan(BaseModel):
    plan_id: str
    request: ExecutionRequest
    simulation: SimulationReport
    policy_validation: PolicyValidationReport
    approval: ApprovalWorkflow
    workflow: ExecutionWorkflow
    status: ExecutionStatus
    result: Optional[ExecutionResult]
    rollback: Optional[RollbackExecution]
    summary: Optional[ExecutionSummary]

class AutonomousCloudOpsReport(BaseModel):
    coverage_report: str
    readiness_report: str
    known_limitations: List[str]
    technical_debt: str
    implementation_status: str
