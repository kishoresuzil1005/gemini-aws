# knowledge/graph/graph_node.py
"""Graph Node wrapper for Canonical entities."""

from typing import Any, List, Dict
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    """Unified wrapper for a CanonicalResource or CanonicalRule."""
    
    node_id: str
    node_type: str        # 'RESOURCE' or 'RULE'
    entity: Any           # Holds CanonicalResource OR CanonicalRule dict/object
    labels: List[str] = Field(default_factory=list) # e.g. ["Security", "AWS", "IAM"]
    properties: Dict[str, Any] = Field(default_factory=dict) # For fast graph-level querying
