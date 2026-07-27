"""GraphNormalizer – converts any graph representation into a canonical model."""

from typing import Any, Dict, List

class GraphNormalizer:
    @staticmethod
    def normalize(raw_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a raw graph payload into a strict canonical structure:
        - Nodes: { id, name, type, properties: {} }
        - Edges: { source, target, relationship }
        """
        if not raw_graph:
            return {"resource": {}, "subgraph": {"nodes": [], "edges": []}}

        subgraph = raw_graph.get("subgraph", {})
        raw_nodes = subgraph.get("nodes", [])
        raw_edges = subgraph.get("edges", [])

        normalized_nodes = []
        for n in raw_nodes:
            if not isinstance(n, dict):
                continue
            
            node_id = n.get("id") or n.get("resource_id") or n.get("_id") or "unknown"
            node_name = n.get("name") or n.get("resource_name") or node_id
            
            node_type = n.get("type") or n.get("resource_type")
            if not node_type and "labels" in n:
                labels = n["labels"]
                if isinstance(labels, list) and len(labels) > 0:
                    node_type = labels[0]
            if not node_type:
                node_type = "Unknown"

            properties = {k: v for k, v in n.items() if k not in ("id", "name", "type")}

            normalized_nodes.append({
                "id": node_id,
                "name": node_name,
                "type": node_type,
                "properties": properties
            })

        normalized_edges = []
        for e in raw_edges:
            if not isinstance(e, dict):
                continue

            source = e.get("source") or e.get("from") or e.get("start")
            target = e.get("target") or e.get("to") or e.get("end")
            relationship = e.get("relationship") or e.get("relation") or e.get("label") or e.get("type") or "UNKNOWN"

            if source and target:
                normalized_edges.append({
                    "source": str(source),
                    "target": str(target),
                    "relationship": str(relationship)
                })

        return {
            "resource": raw_graph.get("resource", {}),
            "subgraph": {
                "nodes": normalized_nodes,
                "edges": normalized_edges
            }
        }
