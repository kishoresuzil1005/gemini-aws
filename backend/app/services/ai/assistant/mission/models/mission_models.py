from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class MissionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class MissionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MissionObjective(BaseModel):
    objective_id: str
    description: str
    status: MissionStatus = MissionStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    workflows: List[str] = Field(default_factory=list)  # Linked workflow IDs

class MissionGoal(BaseModel):
    description: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    objectives: List[MissionObjective] = Field(default_factory=list)

class Mission(BaseModel):
    mission_id: str
    title: str
    intent: str
    status: MissionStatus = MissionStatus.PENDING
    priority: MissionPriority = MissionPriority.MEDIUM
    goal: MissionGoal
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MissionCheckpoint(BaseModel):
    checkpoint_id: str
    mission_id: str
    objective_id: Optional[str] = None
    state: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MissionResult(BaseModel):
    mission_id: str
    status: MissionStatus
    duration_seconds: float
    metrics_achieved: Dict[str, Any]
    insights: List[str