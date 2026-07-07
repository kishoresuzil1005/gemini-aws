from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Message(BaseModel):
    role: str
    content: str

class ConversationContext(BaseModel):
    conversation_id: str
    current_resource: Optional[str] = None
    current_cloud: str = "aws"
    current_region: Optional[str] = None
    current_risk: Optional[str] = None
    current_workflow: Optional[str] = None
    current_recommendation: Optional[str] = None
    current_intent: Optional[str] = None
    current_resource_type: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default_session"

class ChatResponse(BaseModel):
    answer: str
    intent: Optional[str] = None
    resource: Optional[str] = None
    sources: List[str] = []

class ToolResponse(BaseModel):
    tool_name: str
    status: str
    execution_time_ms: int = 0
    confidence: float = 1.0
    context: Any = None
    metadata: Dict[str, Any] = {}
