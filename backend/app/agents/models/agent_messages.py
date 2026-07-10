from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class MessagePayload(BaseModel):
    action: str
    data: Dict[str, Any]

class AgentMessage(BaseModel):
    message_id: str
    sender_id: str
    receiver_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: MessagePayload
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

class EventMessage(BaseModel):
    event_id: str
    event_type: str
    source_agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
