from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_ON_DEPENDENCY = "WAITING_ON_DEPENDENCY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SubTask(BaseModel):
    subtask_id: str
    name: str
    description: str
    assigned_agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list) # List of subtask_ids
    result: Optional[Dict[str, Any]] = None

class AgentTask(BaseModel):
    task_id: str
    title: str
    intent: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    subtasks: List[SubTask] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 1
