"""
Dependency Engine.
Computes Blast Radius, SPOFs, and Isolation logic purely mathematically.
"""
from typing import List, Any, Dict
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.graph.traversal_service import TraversalService
from app.services.ai.analyzers.engines.graph.graph_metrics import GraphMetrics
from app.services.ai.analyzers.engines.dependency.dependency_models import DependencyAnalysis
from app.services.ai.analyzers.engines.dependency.business_criticality_engine import BusinessCriticalityEngine
from app.services.ai.analyzers.engines.dependency.incident_impact_engine import IncidentImpactEngine
from app.services.ai.analyzers.engines.dependency.explainability_engine import ExplainabilityEngine
from app.services.ai.analyzers.engines.dependency.prioritization_engine import PrioritizationEngine

class DependencyEngine:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @classmethod
    def analyze(cls, graph: InfrastructureGraph, index: GraphIndex, node_id: str, cycle: List[str] = None) -> DependencyAnalysis:
        """
        Executes all deterministic dependency algorithms on a single node.
        """
        props = graph.get_node(node_id)
        node_type = props.get("type", "Unknown")
        
        # 1. Isolation & Fan
        in_degree = GraphMetrics.in_degree(index, node_id)
        out_degree = GraphMetrics.out_degree(index, node_id)
        is_isolated = (in_degree == 0 and out_degree == 0)
        
        # 2. Blast Radius (Downstream)
        downstream_nodes = list(TraversalService.bfs(index, node_id, max_depth=5, reverse=False))
        
        # 3. Upstream Impact (Reverse BFS)
        upstream_nodes = list(TraversalService.bfs(index, node_id, max_depth=5, reverse=True))
        
        # 4. Critical Path (True longest path)
        crit_path_down = TraversalService.longest_path(index, node_id, reverse=False)
        crit_path_up = TraversalService.longest_path(index, node_id, reverse=True)
        
        # 5. SPOF Detection (Robust)
        is_spof = False
        redundancy_score = 100
        if in_degree > 0:
            region = props.get("region", "global")
            az = props.get("availability_zone")
            same_type_in_region = [n for n in index.by_type.get(node_type, set()) 
                                   if graph.get_node(n).get("region", "global") == region]
                                   
            if len(same_type_in_region) == 1:
                is_spof = True
                redundancy_score = 0
            elif az:
                # Check AZ level redundancy
                same_type_in_az = [n for n in same_type_in_region if graph.get_node(n).get("availability_zone") == az]
                if len(same_type_in_region) == len(same_type_in_az):
                    # Multi-instance but single AZ
                    is_spof = True
                    redundancy_score = 30
                    
        # 5. Business Criticality & Topology-based Importance
        props = graph.nodes.get(node_id, {})
        crit_data = BusinessCriticalityEngine.calculate(props, blast_radius=len(downstream_nodes), upstream_count=len(upstream_nodes))
        business_criticality = crit_data["tier"]
        scores = crit_data["scores"]
            
        # 7. Cycles / Circular Dependencies
        cycles = []
        if cycle:
            cycles.append(cycle)
        elif cycle is None:
            all_sccs = TraversalService.tarjan_scc(index)
            for scc in all_sccs:
                if node_id in scc and len(scc) > 1:
                    cycles.append(scc)
                    break
            
        analysis = DependencyAnalysis(
            node_id=node_id,
            node_type=str(props.get("type", props.get("resource_type", "Unknown"))),
            blast_radius=len(downstream_nodes),
            upstream_count=len(upstream_nodes),
            dependency_count=in_degree + out_degree,
            fan_in=in_degree,
            fan_out=out_degree,
            dependency_depth=len(crit_path_up) + len(crit_path_down),
            is_spof=is_spof,
            is_isolated=is_isolated,
            business_criticality=business_criticality,
            redundancy_score=100 if not is_spof else 20,
            critical_path_downstream=crit_path_down,
            critical_path_upstream=crit_path_up,
            cycles=cycles,
            criticality_score=scores["business_importance"],
            environment=str(props.get("tags", {}).get("Environment", "Unknown")),
            account=str(props.get("account_id", "Unknown")),
            region=str(props.get("region", "Unknown"))
        )
        
        # 8. Enrich with Incident Impact
        impact = IncidentImpactEngine.evaluate(analysis, downstream_nodes, graph)
        
        # 9. Prioritization
        analysis.priority_score = PrioritizationEngine.calculate_priority_score(analysis, impact)
        
        # 10. Explainability
        explanation = ExplainabilityEngine.generate_explanation(analysis, impact)
        # Store as transient attributes for the analyzer orchestrator
        analysis.__dict__["incident_impact"] = impact
        analysis.__dict__["explanation"] = explanation
        
        return analysis
