from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DependencyNode(BaseModel):
    id: str
    name: str
    type: str
    status: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class DependencyEdge(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class Dependency(BaseModel):
    node: DependencyNode
    edges: List[DependencyEdge]

class DependencyPath(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    total_distance: int

class DependencyGraphView(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]

class DependencyChain(BaseModel):
    chain: List[DependencyNode]
    is_circular: bool = False

class DependencyTree(BaseModel):
    root: DependencyNode
    children: List['DependencyTree'] = Field(default_factory=list)

class DependencyImpact(BaseModel):
    resource_id: str
    impact_type: str  # e.g., 'IMMEDIATE', 'INDIRECT', 'CROSS_ACCOUNT'
    severity: str     # e.g., 'HIGH', 'MEDIUM', 'LOW'
    description: str

class DependencyRisk(BaseModel):
    risk_id: str
    resource_id: str
    score: int
    description: str

class DependencyRecommendation(BaseModel):
    severity: str
    confidence: float
    reason: str
    evidence: str
    affected_resources: List[str]
    suggested_remediation: str

class DependencyFinding(BaseModel):
    title: str
    description: str
    risks: List[DependencyRisk] = Field(default_factory=list)
    recommendations: List[DependencyRecommendation] = Field(default_factory=list)

class RootCause(BaseModel):
    root_dependency: DependencyNode
    failure_type: str
    impacted_resources: List[str]
    narrative: str

class BlastRadius(BaseModel):
    origin: DependencyNode
    impacts: List[DependencyImpact]
    risk_score: int
    affected_resources_count: int

class CriticalPath(BaseModel):
    path: DependencyPath
    bottlenecks: List[DependencyNode]
    single_points_of_failure: List[DependencyNode]

# Rebuild models for recursive references
DependencyTree.update_forward_refs()
