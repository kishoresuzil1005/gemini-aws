"""
Pure Domain Models for Dependency Analysis.
Strictly decoupled from Analyzer framework models.
"""
from typing import List
from pydantic import BaseModel, Field

class DependencyAnalysis(BaseModel):
    """
    Deterministic result of a dependency evaluation.
    """
    node_id: str = Field(...)
    node_type: str = Field(...)
    
    # Impact Metrics
    blast_radius: int = Field(default=0, description="Total number of downstream nodes affected.")
    upstream_count: int = Field(default=0, description="Total number of upstream nodes dependent on this.")
    fan_in: int = Field(default=0, description="Direct upstream dependencies.")
    fan_out: int = Field(default=0, description="Direct downstream dependencies.")
    
    # Findings
    is_spof: bool = Field(default=False, description="True if this acts as a Single Point of Failure.")
    is_isolated: bool = Field(default=False, description="True if this node has no connections.")
    business_criticality: str = Field(default="Standard", description="Mission Critical, Production, etc.")
    redundancy_score: int = Field(default=100, description="Score evaluating high availability.")
    
    # Path Data
    critical_path_downstream: List[str] = Field(default_factory=list, description="True longest downstream dependency chain.")
    critical_path_upstream: List[str] = Field(default_factory=list, description="True longest upstream dependency chain.")
    
    cycles: List[List[str]] = Field(default_factory=list, description="Circular dependency loops involving this node.")
