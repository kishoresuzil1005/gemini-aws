from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from app.services.ai.context_engine.enums import ContextLevel

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

class ExecutionContext(BaseModel):
    """Immutable assistant-layer request state.

    ``ContextRequest`` remains the smaller Context Engine contract generated
    from this model; the two are deliberately not interchangeable.
    """
    model_config = ConfigDict(frozen=True)

    user_message: str
    intent: Optional[str] = None
    identifier: Optional[str] = None
    provider: str = "aws"
    account_id: Optional[str] = None
    region: Optional[str] = None
    analysis_depth: ContextLevel = ContextLevel.STANDARD
    include_metrics: bool = True
    include_cost: bool = True
    include_security: bool = True
    include_graph: bool = True
    include_documentation: bool = True
    include_inventory: bool = True
    session_id: str
    user_role: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ResolvedQuery(BaseModel):
    identifier: Optional[str] = None
    confidence: float = 0.0
    source: str = "none"
    suggestions: List[str] = Field(default_factory=list)
    ambiguity: bool = False
    matched_resource: Optional[Dict[str, Any]] = None
