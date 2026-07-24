"""
Domain Models for the Enterprise Remediation Engine.
"""
from enum import Enum
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict

class RemediationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

class RemediationPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RemediationComplexity(str, Enum):
    TRIVIAL = "TRIVIAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

class ExecutionMode(str, Enum):
    MANUAL = "MANUAL"
    SEMI_AUTOMATIC = "SEMI_AUTOMATIC"
    FULLY_AUTOMATIC = "FULLY_AUTOMATIC"

class RollbackMode(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"
    NONE = "NONE"

class EstimatedDuration(BaseModel):
    model_config = ConfigDict(frozen=True)
    minutes: int
    description: str

class EstimatedDowntime(BaseModel):
    model_config = ConfigDict(frozen=True)
    minutes: int
    is_disruptive: bool

class MaintenanceWindow(BaseModel):
    model_config = ConfigDict(frozen=True)
    required: bool
    recommended_time: Optional[str] = None

class RiskAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)
    level: RemediationPriority
    description: str
    data_loss_risk: bool

class ImpactAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)
    technical_impact: str
    business_impact: str

class ApprovalRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)
    required: bool
    roles: List[str] = Field(default_factory=list)

class ValidationStep(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str
    command: Optional[str] = None
    expected_output: Optional[str] = None

class Command(BaseModel):
    model_config = ConfigDict(frozen=True)
    command: str
    description: str

class AWSCLICommand(Command):
    model_config = ConfigDict(frozen=True)
    service: str

class ShellCommand(Command):
    model_config = ConfigDict(frozen=True)
    is_sudo_required: bool

class TerraformResource(BaseModel):
    model_config = ConfigDict(frozen=True)
    hcl: str
    resource_type: str
    description: str

class CloudFormationResource(BaseModel):
    model_config = ConfigDict(frozen=True)
    yaml: str
    resource_type: str
    description: str
    
class AnsibleTask(BaseModel):
    model_config = ConfigDict(frozen=True)
    yaml: str
    module: str
    description: str

class Runbook(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    steps: List[str] = Field(default_factory=list)

class RollbackPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    mode: RollbackMode
    commands: List[Union[AWSCLICommand, ShellCommand, TerraformResource, CloudFormationResource, AnsibleTask, Runbook]] = Field(default_factory=list)
    description: str

class AutomationCapability(BaseModel):
    model_config = ConfigDict(frozen=True)
    is_automatable: bool
    confidence: float
    reason: str

class ManualTask(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str
    assignee_role: str

class RemediationStep(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    description: str
    actions: List[Union[AWSCLICommand, ShellCommand, TerraformResource, CloudFormationResource, AnsibleTask, Runbook]] = Field(default_factory=list)
    validation: List[ValidationStep] = Field(default_factory=list)
    rollback: RollbackPlan

class RemediationScript(BaseModel):
    model_config = ConfigDict(frozen=True)
    language: str
    content: str

class AutomationPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    capability: AutomationCapability
    mode: ExecutionMode
    script: Optional[RemediationScript] = None

class RemediationAction(BaseModel):
    model_config = ConfigDict(frozen=True)
    action_id: str
    title: str
    description: str
    complexity: RemediationComplexity
    priority: RemediationPriority
    downtime: EstimatedDowntime
    duration: EstimatedDuration
    maintenance_window: MaintenanceWindow
    risk: RiskAssessment
    impact: ImpactAssessment
    approval: ApprovalRequirement
    steps: List[RemediationStep] = Field(default_factory=list)
    automation: AutomationPlan

class RemediationPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    plan_id: str
    finding_id: str
    resource_id: str
    status: RemediationStatus
    actions: List[RemediationAction] = Field(default_factory=list)
    generated_at: float
