# knowledge/graph/graph_edge.py
"""Graph Edge wrapper for Canonical relationships."""

from typing import Any, Dict
from pydantic import BaseModel, Field

class GraphEdge(BaseModel):
    """Unified wrapper for a CanonicalRelationship or virtual edge."""
    
    edge_id: str
    source_id: str
    target_id: str
    relationship_type: str # e.g., 'DEPENDS_ON', 'GOVERNS'
    
    entity: Any = None     # Holds CanonicalRelationship dict/object if it's a physical edge
    weight: float = 1.0    # For shortest path logic
    properties: Dict[str, Any] = Field(default_factory=dict)
