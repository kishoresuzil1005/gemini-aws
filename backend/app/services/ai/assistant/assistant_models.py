from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Message(BaseModel):
    role: str
    content: str

class ResourceMatch(BaseModel):
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    confidence: float = 0.0
    source: str = "none"
    suggestions: List[str] = []

class ConversationContext(BaseModel):
    conversation_id: str
    current_resource: Optional[str] = None
    current_cloud: str = "aws"
    current_region: Optional[str] = None
    current_risk: Optional[str] = None
    current_workflow: Optional[str] = None
    current_recommendation: Optional[str] = None
    current_intent: Optional[str] = None
    last_intent: Optional[str] = None
    current_resource_type: Optional[str] = None
    current_resource_confidence: float = 0.0

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default_session"

class ChatResponse(BaseModel):
    status: str = "success"
    answer: Optional[str] = None
    intent: Optional[str] = None
    resource: Optional[str] = None
    sources: Optional[List[Any]] = None
    confidence: Optional[int] = None
    evidence: Optional[List[str]] = None
    tools_used: Optional[List[str]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    data: Optional[Any] = None

class ToolResponse(BaseModel):
    tool_name: str
    status: str
    execution_time_ms: int = 0
    confidence: float = 1.0
    context: Any = None
    metadata: Dict[str, Any] = {}
