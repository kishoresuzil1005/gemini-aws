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

    # --------------------------------------------------

    def balance_group(
        self,
        nodes,
        relationship_groups,
    ):

        lookup = {
            n["id"]: n
            for n in nodes
        }

        MIN_X = 80

        for parent_id, group in relationship_groups.items():

            parent = lookup.get(parent_id)

            if not parent:
                continue

            children = [
                lookup[c]
                for c in group["children"]
                if c in lookup
            ]

            if not children:
                continue

            #
            # Keep only children on same row
            #

            children = [
                c
                for c in children
                if c["row"] == children[0]["row"]
            ]

            if not children:
                continue

            #
            # Sort by grid column
            #

            children.sort(
                key=lambda n: n["column"]
            )

            #
            # Dynamic spacing
            #

            if len(children) == 1:

                parent["x"] = children[0]["x"]
                continue

            xs = sorted(
                c["x"]
                for c in children
            )

            spacing = min(
                xs[i + 1] - xs[i]
                for i in range(len(xs) - 1)
            )

            if spacing <= 0:
                spacing = 260

            group_width = spacing * (len(children) - 1)

            start = parent["x"] - group_width / 2

            if start < MIN_X:
                start = MIN_X

            x = start

            for child in children:

                child["x"] = x

                x += spacing

        return nodes

    # --------------------------------------------------

    def center_relationship_groups(
        self,
        nodes,
        relationship_groups,
    ):
        """
        Centers parent nodes horizontally over their children.
        Uses sum(xs) / len(xs) for stable averaging.
        """
        lookup = {n["id"]: n for n in nodes}

        for parent_id, group in relationship_groups.items():
            parent = lookup.get(parent_id)
            if not parent:
                continue

            children = [lookup[c] for c in group["children"] if c in lookup]
            if not children:
                continue

            xs = [c["x"] for c in children]
            
            parent["x"] = sum(xs) / len(xs)

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

        nodes = self.center_relationship_groups(
            nodes,
            relationship_groups,
        )

        nodes = self.balance_group(
            nodes,
            relationship_groups,
        )

        nodes = self.snap(nodes)

        return node