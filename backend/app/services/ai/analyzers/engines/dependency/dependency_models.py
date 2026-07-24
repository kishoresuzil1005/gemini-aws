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
    
    # Environment & Ownership
    environment: str = Field(default="Unknown")
    availability_zone: str = Field(default="Unknown")
    region: str = Field(default="Unknown")
    account: str = Field(default="Unknown")
    owners: List[str] = Field(default_factory=list)
    business_services: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    
    # Impact Metrics (Dependency)
    blast_radius: int = Field(default=0, description="Total number of downstream nodes affected.")
    upstream_count: int = Field(default=0, description="Total number of upstream nodes dependent on this.")
    dependency_count: int = Field(default=0, description="Total number of immediate dependencies.")
    fan_in: int = Field(default=0, description="Direct upstream dependencies.")
    fan_out: int = Field(default=0, description="Direct downstream dependencies.")
    dependency_depth: int = Field(default=0, description="Max depth of dependency chain.")
    
    # Core Findings
    is_spof: bool = Field(default=False, description="True if this acts as a Single Point of Failure.")
    is_isolated: bool = Field(default=False, description="True if this node has no connections.")
    business_criticality: str = Field(default="Internal", description="Mission Critical, Production, etc.")
    
    # Deterministic Scores
    criticality_score: int = Field(default=0)
    redundancy_score: int = Field(default=100)
    risk_score: int = Field(default=0)
    blast_radius_score: int = Field(default=0)
    confidence_score: int = Field(default=100)
    root_cause_score: int = Field(default=0)
    priority_score: int = Field(default=0)
    
    # Probabilistic & Lifecycle Estimations (Calculated Deterministically)
    failure_probability: float = Field(default=0.0)
    recovery_complexity: str = Field(default="Low")
    estimated_mttr: int = Field(default=0, description="Estimated Mean Time To Recovery in minutes.")
    estimated_mtbf: int = Field(default=0, description="Estimated Mean Time Between Failures in days.")
    
    # Path Data
    critical_path_downstream: List[str] = Field(default_factory=list)
    critical_path_upstream: List[str] = Field(default_factory=list)
    
    cycles: List[List[str]] = Field(default_factory=list, description="Circular dependency loops involving this node.")
