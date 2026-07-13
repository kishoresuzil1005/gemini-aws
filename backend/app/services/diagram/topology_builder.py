from app.services.diagram.relationship_analyzer import RelationshipAnalyzer

class TopologyBuilder:
    """
    Converts the flat relationship graph into architecture paths/trees.
    """
    
    def __init__(self):
        self.relationships = RelationshipAnalyzer()

    def build(self):
        rel_data = self.relationships.analyze()
        
        node_lookup = {n["id"]: n for n in rel_data["nodes"]}
        parent_to_children = rel_data["parent_to_children"]
        
        def build_tree(node_id, visited):
            if node_id in visited:
                # Break circular references to avoid infinite recursion
                node = node_lookup.get(node_id, {})
                return {
                    "id": node_id,
                    "type": node.get("type", "Unknown"),
                    "name": node.get("name"),
                    "metadata": node.get("metadata", {}),
                    "children": []
                }
                
            visited.add(node_id)
            node = node_lookup.get(node_id)
            
            if not node:
                return None
                
            children = []
            for child_id in parent_to_children.get(node_id, []):
                child_tree = build_tree(child_id, set(visited))
                if child_tree:
                    children.append(child_tree)
                    
            return {
                "id": node_id,
                "type": node["type"],
                "name": node.get("name"),
                "metadata": node.get("metadata", {}),
                "children": children
            }

        topology = []
        for entry in rel_data["entry_nodes"]:
            tree = build_tree(entry["id"], set())
            if tree:
                topology.append(tree)
                
        return {
            "topology": topology
        }