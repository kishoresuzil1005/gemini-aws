from pydantic import BaseModel
from typing import List, Dict, Optional

class ExecutionStep(BaseModel):
    id: str
    title: str
    action: str
    command: str
    estimated_time: str
    rollback: str

class ApprovalRequirement(BaseModel):
    required: bool
    approver_group: str
    reason: str

class RollbackPlan(BaseModel):
    strategy: str
    commands: List[str]

class ValidationPlan(BaseModel):
    check_type: str
    command: str
    expected_result: str

class ExecutionPackage(BaseModel):
    resource_id: str
    issue: str
    risk_level: str
    approval: ApprovalRequirement
    execution_plan: List[ExecutionStep]
    rollback: RollbackPlan
    validation: ValidationPlan
