from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ExecutionStep(BaseModel):
    id: str
    title: str
    action: str
    command: str
    estimated_time: str
    rollback: str

class ApprovalRequirement(BaseModel):
    required: bool
    approver_group: Optional[str]
    reason: str

class RollbackPlan(BaseModel):
    strategy: str
    commands: List[ExecutionStep]

class ValidationPlan(BaseModel):
    check_type: str
    command: str
    expected_result: str

class ExecutionPackage(BaseModel):
    resource_id: str
    issue: str
    risk_level: str
    approval: ApprovalRequirement
    estimated_duration: str
    expected_downtime: str
    automation_level: str
    execution_plan: List[ExecutionStep]
    execution_graph: Dict[str, Any]
    rollback: RollbackPlan
    validation: ValidationPlan