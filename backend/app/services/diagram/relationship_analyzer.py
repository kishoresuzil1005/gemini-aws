from collections import defaultdict

from app.services.diagram.graph_parser import GraphParser
from app.services.diagram.hierarchy_rules import HierarchyRules


class RelationshipAnalyzer:
    """
    Builds a relationship graph from Neo4j resources.

    Responsibilities
    ----------------
    • Parent -> Children
    • Child -> Parent
    • Entry point detection
    • Leaf detection
    """

    ENTRY_TYPES = {

        "InternetGateway",
        "Route53",
        "CloudFront",
        "API Gateway",
        "APIGateway",
        "LoadBalancer",
        "ALB"

    }

    def __init__(self):

        self.graph = GraphParser()

    def analyze(self):

        graph = self.graph.parse()

        parent_to_children = defaultdict(list)
        child_to_parent = defaultdict(list)

        rules = HierarchyRules()

        #
        # Build relationships
        #

        for edge in graph["edges"]:
            parent, child = rules.resolve(edge)

            if parent is None or child is None:
                continue

            if child not in parent_to_children[parent]:
                parent_to_children[parent].append(child)

            if parent not in child_to_parent[child]:
                child_to_parent[child].append(parent)

        #
        # Detect entry nodes
        #

        entry_nodes = []

        for node in graph["nodes"]:

            if node["type"] in self.ENTRY_TYPES:

                entry_nodes.append(node)

            elif node["id"] not in child_to_parent:

                #
                # No incoming edge
                #

                entry_nodes.append(node)

        #
        # Detect leaf nodes
        #

        leaf_nodes = []

        for node in graph["nodes"]:

            if node["id"] not in parent_to_children:

                leaf_nodes.append(node)

        return {
            "nodes": graph["nodes"],
            "edges": graph["edges"],
            "parent_to_children": dict(parent_to_children),
            "child_to_parent": dict(child_to_parent),
            "entry_nodes": entry_nodes,
            "leaf_nodes": leaf_nodes
        