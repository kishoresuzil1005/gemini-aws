from collections import defaultdict

from app.services.diagram.vpc_az_builder import VPCAZBuilder
from app.services.diagram.relationship_analyzer import RelationshipAnalyzer
from app.services.diagram.aws_icon_mapper import AWSIconMapper
from app.services.diagram.relationship_builder import RelationshipBuilder


class SmartLayoutEngine:
    """
    Builds a hierarchical layout from the discovered AWS topology.

    Pipeline

    Relationship Analyzer
            ↓
    VPC Builder
            ↓
    Smart Layout
    """

    NODE_WIDTH = 170
    NODE_HEIGHT = 70

    HORIZONTAL_SPACING = 220
    VERTICAL_SPACING = 140

    LEFT_MARGIN = 120
    TOP_MARGIN = 80

    def __init__(self):

        self.vpc_builder = VPCAZBuilder()

        self.relationships = RelationshipAnalyzer()

        self.icon_mapper = AWSIconMapper()

        self.relationship_builder = RelationshipBuilder()

    def build(self):

        graph = self.relationships.analyze()
        
        # Save parent_children so the builder doesn't erase it
        parent_children = graph.get("parent_to_children", {})

        graph = self.relationship_builder.build(graph)
        graph["parent_to_children"] = parent_children

        hierarchy = self.vpc_builder.build()

        node_lookup = {
            n["id"]: n
            for n in graph["nodes"]
        }

        parent_children = graph["parent_to_children"]

        nodes = []

        edges = graph["edges"]

        visited = set()

        current_x = self.LEFT_MARGIN

        #
        # Layout each VPC
        #

        for vpc in hierarchy["vpcs"]:

            vpc_node = node_lookup.get(vpc["id"])

            if not vpc_node:
                continue

            self._layout_tree(

                node=vpc_node,

                parent_children=parent_children,

                node_lookup=node_lookup,

                nodes=nodes,

                visited=visited,

                x=current_x,

                y=self.TOP_MARGIN,

                depth=0

            )

            current_x += 900

        #
        # Canvas
        #

        max_x = max(
            (n["x"] for n in nodes),
            default=0
        )

        max_y = max(
            (n["y"] for n in nodes),
            default=0
        )

        layout = {

            "canvas": {

                "width": max_x + 400,

                "height": max_y + 250

            },

            "nodes": nodes,

            "edges": edges,
            
            "node_lookup": {n["id"]: n for n in nodes}

        }

        layout["vpcs"] = []

        current_y = 60

        for vpc in hierarchy["vpcs"]:

            vpc_box = {

                "id": vpc["id"],

                "name": vpc.get("name", "VPC"),

                "x": 40,

                "y": current_y,

                "width": 1600,

                "height": 700,

                "availability_zones": []

            }

            az_x = 70

            for az in vpc["availability_zones"]:

                az_box = {

                    "name": az["name"],

                    "x": az_x,

                    "y": current_y + 60,

                    "width": 700,

                    "height": 600,

                    "public_subnets": [],

                    "private_subnets": []

                }

                py = current_y + 110

                for subnet in az["public_subnets"]:

                    az_box["public_subnets"].append({

                        "x": az_x + 20,

                        "y": py,

                        "width": 650,

                        "height": 120

                    })

                    py += 140

                for subnet in az["private_subnets"]:

                    az_box["private_subnets"].append({

                        "x": az_x + 20,

                        "y": py,

                        "width": 650,

                        "height": 180

                    })

                    py += 200

                vpc_box["availability_zones"].append(

                    az_box

                )

                az_x += 760

            layout["vpcs"].append(

                vpc_box

            )

        return layout

    def _layout_tree(

        self,

        node,

        parent_children,

        node_lookup,

        nodes,

        visited,

        x,

        y,

        depth

    ):

        if node["id"] in visited:

            return

        visited.add(node["id"])

        nodes.append({

            "id": node["id"],

            "type": node["type"],

            "display_name": node.get("name") or node["type"],

            "icon": self.icon_mapper.get_icon(

                node["type"]

            ),

            "x": x,

            "y": y,

            "width": self.NODE_WIDTH,

            "height": self.NODE_HEIGHT,

            "depth": depth

        })

        children = parent_children.get(

            node["id"],

            []

        )

        if not children:

            return

        #
        # Spread children horizontally
        #

        total = len(children)

        start_x = x - (

            (total - 1)

            * self.HORIZONTAL_SPACING

        ) / 2

        child_x = start_x

        child_y = y + self.VERTICAL_SPACING

        for child_id in children:

            child = node_lookup.get(child_id)

            if not child:

                continue

            self._layout_tree(

                node=child,

                parent_children=parent_children,

                node_lookup=node_lookup,

                nodes=nodes,

                visited=visited,

                x=child_x,

                y=child_y,

                depth=depth + 1

            )

            child_x += self.HORIZONTAL_SPACING
