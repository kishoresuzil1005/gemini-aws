from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from .base_task import SubTask
from .base_message import AgentMessage

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

class BaseAgent(ABC):
    """
    Base class for all domain agents, ensuring a standard lifecycle and interface.
    """
    def __init__(self, agent_id: str, domain: str):
        self.agent_id = agent_id
        self.domain = domain
        self.state = AgentState(agent_id=agent_id)
        
    def initialize(self):
        """Prepare the agent (e.g. load local memory, establish connections)."""
        print(f"[{self.__class__.__name__}] Initializing...")
        self.state.status = "IDLE"

    @abstractmethod
    def execute(self, task: SubTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Core logic to execute a domain-specific task."""
        pass

    def validate(self, task: SubTask) -> bool:
        """Validate if the task is actionable by this agent."""
        return True

    def publish(self, message: AgentMessage):
        """Send a message to the message bus."""
        # Integration with communication layer
        pass

    def receive(self, message: AgentMessage):
        """Receive a message from the message bus."""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Return the current health state of the agent."""
        return {"status": "HEALTHY", "state": self.state.status}

    def shutdown(self):
        """Cleanly shutdown the agent."""
        print(f"[{self.__class__.__name__}] Shutting down...")
        self.state.status = "OFFLINE"
