from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Finding(BaseModel):
    id: str
    source_tool: str
    description: str
    raw_data: Any

class Evidence(BaseModel):
    id: str
    finding_id: str
    description: str
    confidence: float = 1.0

class Risk(BaseModel):
    id: str
    finding_id: str
    severity: str
    description: str
    score: int = 0

class Conflict(BaseModel):
    id: str
    description: str
    tools_involved: List[str]
    resolved: bool = False
    resolution_reason: Optional[str] = None
    winner: Optional[str] = None

class RecommendationPriority(BaseModel):
    id: str
    description: str
    priority: str
    score: int = 0

class ReasoningResult(BaseModel):
    session_id: str
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    risks: List[Risk] = Field(default_factory=list)
    conflicts: List[Conflict] = Field(default_factory=list)
    recommendations: List[RecommendationPriority] = Field(default_factory=list)
    explanation: str = ""