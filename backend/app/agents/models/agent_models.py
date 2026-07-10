from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentConfig(BaseModel):
    agent_id: str
    name: str
    domain: str
    capabilities: List[str]
    max_concurrent_tasks: int = 5
    is_active: bool = True

class AgentState(BaseModel):
    agent_id: str
    status: str = "IDLE"  # IDLE, WORKING, WAITING, ERROR
    current_task_id: Optional[str] = None
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    performance_score: float = 1.0

class AgentCapability(BaseModel):
    capability_name: str
    description: str
    required_permissions: List[str]
