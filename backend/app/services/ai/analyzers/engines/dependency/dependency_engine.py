"""
Dependency Engine.
Computes Blast Radius, SPOFs, and Isolation logic purely mathematically.
"""
from typing import List, Any
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.graph.traversal_service import TraversalService
from app.services.ai.analyzers.engines.graph.graph_metrics import GraphMetrics
from app.services.ai.analyzers.engines.dependency.dependency_models import DependencyAnalysis

class DependencyEngine:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @classmethod
    def analyze(cls, graph: InfrastructureGraph, index: GraphIndex, node_id: str, all_sccs: List[List[str]] = None) -> DependencyAnalysis:
        """
        Executes all deterministic dependency algorithms on a single node.
        """
        props = graph.get_node(node_id)
        node_type = props.get("type", "Unknown")
        
        # 1. Isolation & Fan
        in_deg = GraphMetrics.in_degree(index, node_id)
        out_deg = GraphMetrics.out_degree(index, node_id)
        is_isolated = (in_deg == 0 and out_deg == 0)
        
        # 2. Blast Radius (Downstream)
        downstream_nodes = list(TraversalService.bfs(index, node_id, max_depth=5, reverse=False))
        blast_radius = len(downstream_nodes)
        
        # 3. Upstream Impact (Reverse BFS)
        upstream_nodes = list(TraversalService.bfs(index, node_id, max_depth=5, reverse=True))
        upstream_count = len(upstream_nodes)
        
        # 4. Critical Path (True longest path)
        crit_path_down = TraversalService.longest_path(index, node_id, reverse=False)
        crit_path_up = TraversalService.longest_path(index, node_id, reverse=True)
        
        # 5. SPOF Detection (Robust)
        # A node is a true SPOF if it has incoming traffic (in_deg > 0)
        # AND it is the only node of its type in its Availability Zone or Region.
        is_spof = False
        redundancy_score = 100
        if in_deg > 0:
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
                    
        # 6. Business Criticality Evaluation
        business_criticality = "Standard"
        tags = props.get("tags", {})
        env = tags.get("Environment", tags.get("environment", "")).lower()
        if blast_radius > 50 or env == "production" or env == "prod":
            business_criticality = "Mission Critical"
        elif blast_radius > 20:
            business_criticality = "Production"
            
        # 7. Cycles / Circular Dependencies
        cycles = []
        if all_sccs is None:
            all_sccs = TraversalService.tarjan_scc(index)
        for scc in all_sccs:
            if node_id in scc and len(scc) > 1:
                cycles.append(scc)
            
        return DependencyAnalysis(
            node_id=node_id,
            node_type=node_type,
            blast_radius=blast_radius,
            upstream_count=upstream_count,
            fan_in=in_deg,
            fan_out=out_deg,
            is_spof=is_spof,
            is_isolated=is_isolated,
            business_criticality=business_criticality,
            redundancy_score=redundancy_score,
            critical_path_downstream=crit_path_down,
            critical_path_upstream=crit_path_up,
            cycles=cycles
        )
