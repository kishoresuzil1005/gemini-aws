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

    def center_children(
        self,
        nodes,
        edges,
    ):

        lookup = {
            n["id"]: n
            for n in nodes
        }

        children = defaultdict(list)

        for edge in edges:

            children[
                edge["target"]
            ].append(
                edge["source"]
            )

        for parent_id, child_ids in children.items():

            parent = lookup.get(parent_id)

            if not parent:
                continue

            xs = []

            for child_id in child_ids:

                child = lookup.get(child_id)

                if child:

                    xs.append(child["x"])

            if not xs:
                continue

            #
            # Only move horizontally
            #

            parent["x"] = (
                min(xs)
                + max(xs)
            ) / 2

            #
            # DO NOT TOUCH parent["y"]
            #

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
        edges,
    ):

        nodes = self.align_rows(nodes)

        nodes = self.align_columns(nodes)

        nodes = self.equal_spacing(nodes)

        nodes = self.center_children(
            nodes,
            edges,
        )

        nodes = self.lock_layers(nodes)

        nodes = self.snap(nodes)

        return nodes
