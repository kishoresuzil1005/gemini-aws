from pydantic import BaseModel
from typing import Dict, Any, Optional

class GraphNodeType(BaseModel):
    pass

class GraphEdgeType(BaseModel):
    pass

class CloudNode(BaseModel):
    """A single infrastructure component in the Knowledge Graph."""
    node_id: str
    provider: str
    resource_type: str
    resource_name: str
    properties: Dict[str, Any] = {}

class CloudEdge(BaseModel):
    """A relationship between two CloudNodes."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = {}

class GraphQuery(BaseModel):
    pass

class GraphResult(BaseModel):
    pass

class Dependency(BaseModel):
    pass

class Topology(BaseModel):
    pass

class ImpactResult(BaseModel):
    pass

class BlastRadius(BaseModel):
    pass

class ServiceMap(BaseModel):
    pass

class ResourceOwner(BaseModel):
    pass

class Lineage(BaseModel):
    pass