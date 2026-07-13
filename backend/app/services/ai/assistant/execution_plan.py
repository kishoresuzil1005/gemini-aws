from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class PlanStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class ToolStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"

class ExecutionContext(BaseModel):
    conversation_id: str
    request_id: str
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    intent: str
    priority: int = 1
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolResult(BaseModel):
    tool_name: str
    status: ToolStatus
    started_at: datetime
    finished_at: datetime
    execution_time_ms: int
    context: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolRequirement(BaseModel):
    tool_name: str
    required: bool = True
    timeout: int = 30
    retry_count: int = 0
    parallelizable: bool = False

class ExecutionStep(BaseModel):
    step_number: int
    tool_name: str
    purpose: str
    depends_on: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    optional: bool = False

class ExecutionPlan(BaseModel):
    plan_id: str
    objective: str
    context: ExecutionContext
    status: PlanStatus = PlanStatus.PENDING
    required_tools: List[ToolRequirement] = Field(default_factory=list)
    steps: List[ExecutionStep] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    estimated_steps: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)