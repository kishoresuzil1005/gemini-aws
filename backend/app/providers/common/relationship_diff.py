from typing import List, Dict, Any, Tuple

class RelationshipDiffEngine:
    """
    Calculates differences between old graph relationships and new discovery relationships.
    Prevents rebuilding the Neo4j graph relationships from scratch.
    """
    def calculate_diff(self, old_edges: List[Dict[str, Any]], new_edges: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        # Edges represented as { 'source': id, 'target': id, 'type': 'DEPENDS_ON' }
        def edge_signature(e):
            return f"{e.get('source')}_{e.get('type')}_{e.get('target')}"

        old_map = {edge_signature(e): e for e in old_edges}
        new_map = {edge_signature(e): e for e in new_edges}

        added = []
        removed = []
        changed = [] # Metadata on edges could change

        for sig, e_data in new_map.items():
            if sig not in old_map:
                added.append(e_data)
            elif old_map[sig] != e_data:
                changed.append(e_data)

        for sig, e_data in old_map.items():
            if sig not in new_map:
                removed.append(e_data)

        return {
            "added_edges": added,
            "removed_edges": removed,
            "changed_edges": changed
        }
