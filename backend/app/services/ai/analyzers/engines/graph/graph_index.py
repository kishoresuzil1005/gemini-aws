"""
Graph Indexer.
Builds permanent, reusable structures for O(1) lookups.
"""
from typing import Dict, List, Set, Any
from pydantic import BaseModel, Field
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph

class GraphIndex(BaseModel):
    """Permanent reusable structures."""
    adjacency: Dict[str, Set[str]] = Field(default_factory=dict)
    reverse_adjacency: Dict[str, Set[str]] = Field(default_factory=dict)
    edge_types: Dict[str, Dict[str, str]] = Field(default_factory=dict) # src->tgt : type
    by_type: Dict[str, Set[str]] = Field(default_factory=dict)
    by_region: Dict[str, Set[str]] = Field(default_factory=dict)
    by_owner: Dict[str, Set[str]] = Field(default_factory=dict)
    by_account: Dict[str, Set[str]] = Field(default_factory=dict)
    by_tag: Dict[str, Dict[str, Set[str]]] = Field(default_factory=dict) # key -> value -> set of nodes

    @classmethod
    def version(cls) -> str:
        return "1.0.0"

    @classmethod
    def build(cls, graph: InfrastructureGraph) -> "GraphIndex":
        """Builds all indexes from the InfrastructureGraph."""
        idx = cls()
        
        # Build Adjacency
        for edge in graph.edges:
            src = edge.get("source")
            tgt = edge.get("target")
            etype = edge.get("type", "RELATES_TO")
            
            if not src or not tgt:
                continue
                
            if src not in idx.adjacency:
                idx.adjacency[src] = set()
            idx.adjacency[src].add(tgt)
            
            if tgt not in idx.reverse_adjacency:
                idx.reverse_adjacency[tgt] = set()
            idx.reverse_adjacency[tgt].add(src)
            
            edge_key = f"{src}->{tgt}"
            idx.edge_types[edge_key] = etype

        # Build Metadata Indexes
        for node_id, props in graph.nodes.items():
            # Type Index
            ntype = props.get("type", props.get("resource_type", "Unknown"))
            if ntype not in idx.by_type:
                idx.by_type[ntype] = set()
            idx.by_type[ntype].add(node_id)
            
            # Region Index
            region = props.get("region", "global")
            if region not in idx.by_region:
                idx.by_region[region] = set()
            idx.by_region[region].add(node_id)
            
            # Owner Index
            tags = props.get("tags", {})
            owner = tags.get("Owner", tags.get("owner", "Unowned"))
            if owner not in idx.by_owner:
                idx.by_owner[owner] = set()
            idx.by_owner[owner].add(node_id)
            
            # Account Index
            account = props.get("account_id", props.get("account", "unknown"))
            if account not in idx.by_account:
                idx.by_account[account] = set()
            idx.by_account[account].add(node_id)
            
            # Tags Index
            for k, v in tags.items():
                if k not in idx.by_tag:
                    idx.by_tag[k] = {}
                v_str = str(v)
                if v_str not in idx.by_tag[k]:
                    idx.by_tag[k][v_str] = set()
                idx.by_tag[k][v_str].add(node_id)
            
        return idx
