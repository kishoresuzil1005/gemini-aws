from collections import defaultdict


class AlignmentEngine:
    """
    Generic alignment engine.

    Responsibilities
    ----------------
    - Horizontal alignment
    - Vertical alignment
    - Parent-child centering
    - Equal spacing

    Does NOT know anything about AWS.
    """

    GRID_X = 20
    GRID_Y = 20

    TOP_MARGIN = 80
    LAYER_HEIGHT = 220

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def lock_layers(self, nodes):

        for node in nodes:

            layer = node.get("layer")

            if layer is None:
                continue

            node["y"] = (
                self.TOP_MARGIN
                + layer * self.LAYER_HEIGHT
            )

        return nodes

    # ---------------------------------------------------------

    def align_rows(self, nodes):

        rows = defaultdict(list)

        for node in nodes:
            rows[node["row"]].append(node)

        for row_nodes in rows.values():

            y = min(n["y"] for n in row_nodes)

            for node in row_nodes:
                node["y"] = y

        return nodes

    # ---------------------------------------------------------

    def align_columns(self, nodes):

        cols = defaultdict(list)

        for node in nodes:
            cols[node["column"]].append(node)

        for col_nodes in cols.values():

            x = min(n["x"] for n in col_nodes)

            for node in col_nodes:
                node["x"] = x

        return nodes

    # ---------------------------------------------------------

    def equal_spacing(self, nodes):

        rows = defaultdict(list)

        for node in nodes:
            rows[node["row"]].append(node)

        for row_nodes in rows.values():

            row_nodes.sort(key=lambda n: n["column"])

            if len(row_nodes) < 2:
                continue

            spacing = (
                row_nodes[1]["x"]
                - row_nodes[0]["x"]
            )

            current = row_nodes[0]["x"]

            for node in row_nodes:

                node["x"] = current

                current += spacing

        return nodes

    # ---------------------------------------------------------

    def center_relationship_groups(
        self,
        nodes,
        relationship_groups,
    ):

        lookup = {
            n["id"]: n
            for n in nodes
        }

        for parent_id, children in relationship_groups.items():

            parent = lookup.get(parent_id)

            if not parent:
                continue

            child_nodes = [
                lookup[c]
                for c in children
                if c in lookup
            ]

            if not child_nodes:
                continue

            #
            # Only children in SAME LAYER
            #

            same_layer = [

                c

                for c in child_nodes

                if c["layer"] == child_nodes[0]["layer"]

            ]

            xs = [

                c["x"]

                for c in same_layer

            ]

            if not xs:
                continue

            parent["x"] = (

                min(xs)

                + max(xs)

            ) / 2

        return nodes

    # ---------------------------------------------------------

    def balance_group(
        self,
        nodes,
        relationship_groups
    ):

        lookup = {
            n["id"]: n
            for n in nodes
        }

        for parent_id, children in relationship_groups.items():

            parent = lookup.get(parent_id)

            if not parent:
                continue

            children = [
                lookup[c]
                for c in children
                if c in lookup
            ]

            children.sort(
                key=lambda n:n["x"]
            )

            spacing = 220

            start = (

                parent["x"]

                - spacing * (len(children)-1)/2

            )

            x = start

            for child in children:

                child["x"] = x

                x += spacing

        return nodes

    # ---------------------------------------------------------

    def snap(self, nodes):

        for node in nodes:

            node["x"] = round(
                node["x"] / self.GRID_X
            ) * self.GRID_X

            node["y"] = round(
                node["y"] / self.GRID_Y
            ) * self.GRID_Y

        return nodes

    # ---------------------------------------------------------

    def build(
        self,
        nodes,
        relationship_groups,
    ):

        nodes = self.align_rows(nodes)

        nodes = self.align_columns(nodes)

        nodes = self.equal_spacing(nodes)

        nodes = self.center_relationship_groups(
            nodes,
            relationship_groups,
        )

        nodes = self.balance_group(
            nodes,
            relationship_groups,
        )

        nodes = self.lock_layers(nodes)

        nodes = self.snap(nodes)

        return nodes
