from pydantic import BaseModel
from typing import Dict, Any

class GraphEvent(BaseModel):
    event_type: str
    version: int
    payload: Dict[str, Any]

class NodeEvent(GraphEvent):
    node_id: str
    action: str # added, updated, removed

class RelationshipEvent(GraphEvent):
    edge_signature: str
    action: str