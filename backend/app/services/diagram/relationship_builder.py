from collections import defaultdict

from app.services.diagram.hierarchy_rules import HierarchyRules


class RelationshipBuilder:
    """
    Cleans and enriches graph relationships.

    Responsibilities
    ----------------
    • Remove duplicate edges
    • Remove self-loops
    • Ignore missing nodes
    • Normalize relationship names
    • Build adjacency indexes
    """

    def build(self, graph: dict):

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        #
        # Node lookup
        #

        node_ids = {
            node["id"]
            for node in nodes
        }

        #
        # Relationship indexes
        #

        outgoing = defaultdict(list)
        incoming = defaultdict(list)

        #
        # Deduplicate edges
        #

        seen = set()

        cleaned_edges = []

        for edge in edges:

            source = edge.get("source")
            target = edge.get("target")

            #
            # Ignore invalid nodes
            #

            if source not in node_ids:
                continue

            if target not in node_ids:
                continue

            #
            # Ignore self loop
            #

            if source == target:
                continue

            relation = (
                edge.get("relationship")
                or edge.get("relation")
                or edge.get("type")
                or "RELATED_TO"
            ).upper()

            key = (
                source,
                target,
                relation
            )

            #
            # Remove duplicates
            #

            if key in seen:
                continue

            seen.add(key)

            edge_obj = {

                "source": source,

                "target": target,

                "relationship": relation

            }

            cleaned_edges.append(edge_obj)

            outgoing[source].append(edge_obj)

            incoming[target].append(edge_obj)

        #
        # Statistics
        #

        relationship_groups = {}
        children_graph = defaultdict(list)
        parents_graph = defaultdict(list)
        
        hierarchy_children = defaultdict(list)
        hierarchy_parents = defaultdict(list)
        
        rules = HierarchyRules()

        HIERARCHY_RELATIONSHIPS = {
            "IN_VPC",
            "IN_SUBNET",
            "MEMBER_OF",
            "CONTAINS",
        }

        for edge in cleaned_edges:
            target = edge["target"]
            source = edge["source"]
            relationship = edge["relationship"]
            
            if target not in relationship_groups:
                relationship_groups[target] = {
                    "relationship": relationship,
                    "children": []
                }
            relationship_groups[target]["children"].append(source)
            
            children_graph[source].append(edge)
            parents_graph[target].append(edge)

            if relationship in HIERARCHY_RELATIONSHIPS:
                parent, child = rules.resolve(edge)
                hierarchy_children[parent].append(child)
                hierarchy_parents[child].append(parent)

        return {

            "nodes": nodes,

            "edges": cleaned_edges,

            "outgoing": dict(outgoing),

            "incoming": dict(incoming),
            
            "relationship_groups": dict(relationship_groups),
            
            "children": dict(children_graph),
            
            "parents": dict(parents_graph),

            "hierarchy_children": hierarchy_children,

            "hierarchy_parents": hierarchy_parents,

            "statistics": {

                "nodes": len(nodes),

                "edges": len(cleaned_edges)

            }

        }
