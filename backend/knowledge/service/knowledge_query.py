# knowledge/service/knowledge_query.py
"""Standardized Query Object."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field

class KnowledgeQuery(BaseModel):
    """A standard query payload for complex searches."""
    filters: Dict[str, Any] = Field(default_factory=dict)
    projection: List[str] = Field(default_factory=list)
    limit: int = 100
    offset: int = 0
