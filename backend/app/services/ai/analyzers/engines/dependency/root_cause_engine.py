"""
Root Cause Engine.
Analyzes dependencies deterministically to find likely root causes of failures.
"""
from typing import List, Dict, Any
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.dependency.dependency_models import DependencyAnalysis

class RootCauseEngine:
    
    @classmethod
    def analyze(cls, graph: InfrastructureGraph, index: GraphIndex, node_id: str, analysis: DependencyAnalysis) -> Dict[str, Any]:
        """
        Deterministically evaluates the root cause candidates.
        """
        causes = []
        confidence = "Low"
        
        # Check Cycles
        if analysis.cycles:
            for cycle in analysis.cycles:
                causes.append(f"Circular dependency detected between: {', '.join(cycle)}")
            confidence = "High"
            
        # Check Upstream Critical Path
        if analysis.critical_path_upstream:
            deepest_node = analysis.critical_path_upstream[-1]
            if deepest_node != node_id:
                node_props = graph.get_node(deepest_node)
                ntype = node_props.get("type", "Resource")
                causes.append(f"Upstream failure originating at {ntype} ({deepest_node})")
                confidence = "Medium"
                
        # Check SPOF behavior
        if analysis.is_spof:
            causes.append(f"Single Point of Failure: No redundancy for {analysis.node_type} in this availability zone/region.")
            confidence = "High"
            
        if not causes:
            causes.append("Independent failure. No upstream root cause identified.")
            
        return {
            "likely_causes": causes,
            "confidence": confidence,
            "upstream_path": analysis.critical_path_upstream
        }
