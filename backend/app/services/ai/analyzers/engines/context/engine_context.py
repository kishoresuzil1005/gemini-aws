"""
Unified Engine Context.
The single object passed to all engines, containing the graph and all supplemental data.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph

class EngineContext(BaseModel):
    graph: InfrastructureGraph = Field(...)
    inventory: Dict[str, Any] = Field(default_factory=dict)
    policies: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    configuration: Dict[str, Any] = Field(default_factory=dict)
    telemetry: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata like TraceID.")
