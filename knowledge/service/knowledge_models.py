# knowledge/service/knowledge_models.py
"""Unified models for API responses and envelopes."""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

class Pagination(BaseModel):
    limit: int
    offset: int
    total: int
    has_next: bool

class KnowledgeResponse(BaseModel):
    """Standard envelope for all service replies."""
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pagination: Optional[Pagination] = None
    cache_hit: bool = False
    duration_ms: int = 0
    errors: List[str] = Field(default_factory=list)
