from collections import defaultdict


class SpacingEngine:
    """
    Enforces minimum spacing, resolves overlaps, and handles padding.
    Runs after AlignmentEngine to fix physical collisions.
    """

    MIN_X_SPACING = 220
    MIN_Y_SPACING = 220

    def __init__(self):
        pass

    def build(self, nodes):
        """
        Executes collision resolution.
        """
        nodes = self.resolve_horizontal_overlaps(nodes)
        # Vertical overlaps are inherently resolved by the grid mapping, 
        # but could be expanded here if custom Y adjustments are needed.
        return nodes

    def resolve_horizontal_overlaps(self, nodes):
        """
        Checks for overlapping X coordinates on the same row and pushes nodes right.
        """
        rows = defaultdict(list)
        for node in nodes:
            rows[node.get("row", 0)].append(node)

        for row_index in sorted(rows.keys()):
            row_nodes = rows[row_index]
            
            # Sort strictly by X to process left-to-right
            row_nodes.sort(key=lambda n: n.get("x", 0))

            for i in range(1, len(row_nodes)):
                prev = row_nodes[i - 1]
                curr = row_nodes[i]

                # Check if current node is overlapping or too close to previous node
                expected_min_x = prev["x"] + self.MIN_X_SPACING

                if curr["x"] < expected_min_x:
                    curr["x"] = expected_min_x

        return nodes
