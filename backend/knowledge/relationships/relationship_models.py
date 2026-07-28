# knowledge/relationships/relationship_models.py
"""The central CanonicalRelationship schema and types."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class CanonicalRelationship(BaseModel):
    """The authoritative definition of an edge in the Knowledge Platform."""
    
    relationship_id: str
    relationship_type: str        # e.g., "DEPENDS_ON", "ASSUMES_ROLE"
    
    source_resource_id: str
    target_resource_id: str
    
    provider: str
    service: str
    
    direction: str = "OUTBOUND"   # OUTBOUND, INBOUND, BIDIRECTIONAL
    strength: str = "STRONG"      # STRONG, WEAK
    cardinality: str = "1:1"      # 1:1, 1:N, N:M
    
    status: str = "ACTIVE"
    confidence: float = 1.0
    version: str = "1.0"
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Dict[str, str] = Field(default_factory=dict)
    documentation_references: List[str] = Field(default_factory=list)
    
    creation_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    update_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
