"""
Graph Processor.
Validates, normalizes, and repairs raw graph data before it enters the engines.
"""
from typing import Dict, Any, List
import logging
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph

logger = logging.getLogger(__name__)

class GraphProcessor:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @classmethod
    def process(cls, raw_nodes: List[Dict[str, Any]], raw_edges: List[Dict[str, Any]]) -> InfrastructureGraph:
        """
        Takes raw nodes and edges, repairs them, and returns a clean InfrastructureGraph.
        """
        nodes_map = {}
        for n in raw_nodes:
            nid = str(n.get("id") or n.get("arn") or n.get("name", ""))
            if not nid:
                continue
            
            # Normalize region
            if "region" not in n:
                n["region"] = "global"
                
            nodes_map[nid] = n
            
        clean_edges = []
        for e in raw_edges:
            src = str(e.get("source", ""))
            tgt = str(e.get("target", ""))
            
            # Repair: Remove self loops
            if src == tgt:
                continue
                
            # Repair: Remove broken edges
            if src not in nodes_map or tgt not in nodes_map:
                logger.warning(f"GraphProcessor: Removing broken edge {src} -> {tgt}")
                continue
                
            clean_edges.append(e)
            
        return InfrastructureGraph(nodes=nodes_map, edges=clean_edges)
