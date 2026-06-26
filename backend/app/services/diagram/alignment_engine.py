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

    def __init__(self):
        pass

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
                edge["source"]
            ].append(edge["target"])

        for parent, child_ids in children.items():

            if parent not in lookup:
                continue

            if not child_ids:
                continue

            xs = []

            for cid in child_ids:

                child = lookup.get(cid)

                if child:

                    xs.append(child["x"])

            if not xs:
                continue

            center = (
                min(xs)
                + max(xs)
            ) / 2

            lookup[parent]["x"] = center

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

        nodes = self.snap(nodes)

        return nodes
