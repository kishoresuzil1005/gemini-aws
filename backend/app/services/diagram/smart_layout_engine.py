from collections import defaultdict
import math


from app.services.diagram.vpc_az_builder import VPCAZBuilder
from app.services.diagram.relationship_analyzer import RelationshipAnalyzer
from app.services.diagram.aws_icon_mapper import AWSIconMapper
from app.services.diagram.relationship_builder import RelationshipBuilder
from app.services.diagram.grid_engine import GridEngine
from app.services.diagram.alignment_engine import AlignmentEngine
from app.services.diagram.spacing_engine import SpacingEngine
from app.services.diagram.hierarchy_engine import HierarchyEngine


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

    NODE_WIDTH = 180
    NODE_HEIGHT = 110

    HORIZONTAL_SPACING = 220
    VERTICAL_SPACING = 140

    LEFT_MARGIN = 120
    TOP_MARGIN = 80

    def __init__(self):

        self.vpc_builder = VPCAZBuilder()

        self.relationships = RelationshipAnalyzer()

        self.icon_mapper = AWSIconMapper()

        self.relationship_builder = RelationshipBuilder()

        self.grid = GridEngine()

        self.alignment = AlignmentEngine()

        self.spacing = SpacingEngine()

        self.hierarchy_engine = HierarchyEngine()

    def build(self):

        graph = self.relationships.analyze()
        
        # Save parent_children so the builder doesn't erase it
        parent_children = graph.get("parent_to_children", {})

        graph = self.relationship_builder.build(graph)
        graph["parent_to_children"] = parent_children

        hierarchy = self.vpc_builder.build()

        hierarchy_layers = self.hierarchy_engine.assign_layers(graph)

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

                hierarchy_layers=hierarchy_layers

            )

            current_x += 900

        #
        # Layout all remaining resources that were not placed
        #

        orphan_x = self.LEFT_MARGIN

        for node in graph["nodes"]:

            if node["id"] in visited:
                continue

            self._layout_tree(
                node=node,
                parent_children=parent_children,
                node_lookup=node_lookup,
                nodes=nodes,
                visited=visited,
                x=orphan_x,
                y=self.TOP_MARGIN,
                hierarchy_layers=hierarchy_layers
            )

            orphan_x += self.HORIZONTAL_SPACING

            if orphan_x > 3000:
                orphan_x = self.LEFT_MARGIN

        #
        # Grid Engine positioning
        #

        grid_out = self.grid.build(nodes)

        nodes = grid_out["nodes"]
        canvas = grid_out["canvas"]

        nodes = self.alignment.build(
            nodes,
            graph["relationship_groups"],
        )

        nodes = self.spacing.build(nodes)

        layout = {
            "canvas": {
                "width": canvas["width"],
                "height": canvas["height"]
            },
            "nodes": nodes,
            "edges": edges,
            "node_lookup": {n["id"]: n for n in nodes}
        }

        layout["vpcs"] = []

        #
        # Deduplicate VPCs
        #
        unique_vpcs = []
        drawn_vpcs = set()
        for vpc in hierarchy["vpcs"]:
            if vpc["id"] in drawn_vpcs:
                continue
            drawn_vpcs.add(vpc["id"])
            unique_vpcs.append(vpc)

        VPCS_PER_ROW = 3
        VPC_WIDTH = 1600
        VPC_HEIGHT = 700
        H_GAP = 120
        V_GAP = 120

        for index, vpc in enumerate(unique_vpcs):

            row = index // VPCS_PER_ROW
            col = index % VPCS_PER_ROW

            x = 40 + col * (VPC_WIDTH + H_GAP)
            y = 60 + row * (VPC_HEIGHT + V_GAP)


            vpc_box = {
                "id": vpc["id"],
                "name": vpc.get("name", "VPC"),
                "x": x,
                "y": y,
                "width": VPC_WIDTH,
                "height": VPC_HEIGHT,
                "availability_zones": []
            }

            az_x = x + 30


            for az in vpc["availability_zones"]:

                az_box = {
                    "name": az["name"],
                    "x": az_x,
                    "y": y + 60,
                    "width": 700,
                    "height": 600,
                    "public_subnets": [],
                    "private_subnets": []
                }

                py = y + 110

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

            layout["vpcs"].append(vpc_box)

        # Dynamic Canvas
        rows = math.ceil(len(unique_vpcs) / VPCS_PER_ROW) if unique_vpcs else 1
        svg_width = (VPCS_PER_ROW * (VPC_WIDTH + H_GAP)) + 80
        svg_height = (rows * (VPC_HEIGHT + V_GAP)) + 120

        layout["canvas"]["width"] = max(layout["canvas"]["width"], svg_width)
        layout["canvas"]["height"] = max(layout["canvas"]["height"], svg_height)

        print("================================")
        print("SMART LAYOUT")
        print("Nodes :", len(layout["nodes"]))
        print("Edges :", len(layout["edges"]))
        print("================================")

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

        hierarchy_layers

    ):

        if node["id"] in visited:

            return

        visited.add(node["id"])

        layer = hierarchy_layers.get(node["id"], 0)
        actual_y = self.TOP_MARGIN + layer * self.VERTICAL_SPACING

        nodes.append({

            "id": node["id"],

            "type": node["type"],

            "display_name": node.get("name") or node["type"],

            "icon": self.icon_mapper.get_icon(

                node["type"]

            ),

            "x": x,

            "y": actual_y,

            "width": self.NODE_WIDTH,

            "height": self.NODE_HEIGHT,

            "row": layer

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

                hierarchy_layers=hierarchy_layers

            )

            child_x += self.HORIZONTAL_SPACING
