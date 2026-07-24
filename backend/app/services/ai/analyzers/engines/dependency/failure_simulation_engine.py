"""
Failure Simulation Engine.
Deterministically simulates a failure and calculates the exact blast radius, affected services, and recovery priority.
"""
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.graph.traversal_service import TraversalService
from app.services.ai.analyzers.engines.dependency.business_criticality_engine import BusinessCriticalityEngine
from app.services.ai.analyzers.engines.scoring.scoring_engine import ScoringEngine

class FailureSimulationResult(BaseModel):
    node_id: str
    resources_affected: List[str]
    blast_radius: int
    business_impact: str
    service_impact: List[str]
    recovery_priority: str
    risk_level: str

class FailureSimulationEngine:
    
    @classmethod
    def simulate(cls, graph: InfrastructureGraph, index: GraphIndex, node_id: str) -> FailureSimulationResult:
        """
        Simulates what happens if the given node_id goes down.
        """
        props = graph.get_node(node_id)
        
        # 1. Determine affected resources (Downstream)
        affected_nodes = list(TraversalService.bfs(index, node_id, max_depth=10, reverse=False))
        blast_radius = len(affected_nodes)
        
        # 2. Determine Service Impact (Grouping affected nodes by type)
        impacted_types = {}
        for nid in affected_nodes:
            n_props = graph.get_node(nid)
            ntype = n_props.get("type", "Unknown")
            impacted_types[ntype] = impacted_types.get(ntype, 0) + 1
            
        service_impact = [f"{count} {ntype}(s) degraded" for ntype, count in impacted_types.items()]
        
        # 3. Calculate Business Impact & Risk
        upstream_count = len(list(TraversalService.bfs(index, node_id, max_depth=5, reverse=True)))
        criticality = BusinessCriticalityEngine.calculate(props, blast_radius, upstream_count)
        
        # Determine Recovery Priority
        priority = "Medium"
        if criticality == "Mission Critical" or blast_radius > 50:
            priority = "Critical"
        elif criticality == "Production" or blast_radius > 10:
            priority = "High"
            
        # 4. Calculate Risk
        risk = ScoringEngine.calculate_risk(blast_radius, is_spof=True, is_isolated=False)
        
        return FailureSimulationResult(
            node_id=node_id,
            resources_affected=affected_nodes,
            blast_radius=blast_radius,
            business_impact=f"Failure cascades to {blast_radius} resources affecting {criticality} environments.",
            service_impact=service_impact,
            recovery_priority=priority,
            risk_level=risk.level.name
        )
