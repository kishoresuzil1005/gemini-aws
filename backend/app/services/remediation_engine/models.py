from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

class RemediationRequest(BaseModel):
    request_id: str
    target_id: str
    query: str
    timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

class RemediationDependency(BaseModel):
    dependency_id: str
    status: str

class RemediationRisk(BaseModel):
    risk_type: str
    severity: str
    mitigation_strategy: str

class RollbackPlan(BaseModel):
    rollback_strategy: str
    rollback_order: List[str]
    rollback_dependencies: List[str]
    rollback_validation: List[str]
    success_criteria: List[str]
    rollback_risk: str

class ValidationPlan(BaseModel):
    pre_validation: List[str]
    post_validation: List[str]
    smoke_tests: List[str]
    health_checks: List[str]
    dependency_validation: List[str]
    business_validation: List[str]

class ExecutionPrerequisite(BaseModel):
    name: str
    satisfied: bool

class ExecutionConstraint(BaseModel):
    name: str
    description: str

class ApprovalRequirement(BaseModel):
    approval_required: bool
    change_type: str # Emergency Change, Standard Change, High Risk Change, Low Risk Change
    business_approval: bool
    security_approval: bool
    operations_approval: bool

class MaintenanceRequirement(BaseModel):
    requires_downtime: bool
    estimated_downtime_minutes: int

class ExecutionWindow(BaseModel):
    maintenance_window: str
    business_window: str
    blackout_window: str
    risk_window: str
    regional_constraints: List[str]
    operational_constraints: List[str]

class RemediationStep(BaseModel):
    step_id: str
    action: str
    target: str

class ChangePlan(BaseModel):
    infrastructure_changes: List[str]
    configuration_changes: List[str]
    security_changes: List[str]
    iam_changes: List[str]
    network_changes: List[str]
    database_changes: List[str]
    application_changes: List[str]

class RemediationWorkflow(BaseModel):
    workflow_id: str
    steps: List[RemediationStep]
    change_plan: ChangePlan

class ExecutionReadinessReport(BaseModel):
    permissions_verified: bool
    dependencies_verified: bool
    backups_verified: bool
    snapshots_verified: bool
    recovery_points_verified: bool
    monitoring_verified: bool
    alerting_verified: bool
    rollback_readiness_verified: bool
    ready_for_execution: bool

class RemediationSummary(BaseModel):
    executive_plan: str
    technical_plan: str
    implementation_plan: str
    rollback_plan: str
    validation_plan: str
    approval_plan: str
    risk_summary: str
    business_summary: str

class RemediationPlan(BaseModel):
    plan_id: str
    target_id: str
    workflow: RemediationWorkflow
    execution_order: List[str]
    dependencies: List[RemediationDependency]
    required_services: List[str]
    affected_resources: List[str]
    affected_applications: List[str]
    business_impact: str
    risk_assessment: RemediationRisk
    rollback_plan: RollbackPlan
    validation_plan: ValidationPlan
    approval_requirement: ApprovalRequirement
    execution_window: ExecutionWindow
    execution_readiness: ExecutionReadinessReport
    summary: RemediationSummary

class RemediationImplementationReport(BaseModel):
    coverage_report: str
    readiness_report: str
    technical_debt: str
    known_limitations: List[str]
    implementation_status: str
