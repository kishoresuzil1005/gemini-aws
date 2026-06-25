class EdgeRenderer:
    """
    Responsible ONLY for rendering relationships between resources.

    Supports orthogonal routing.
    """

    EDGE_COLOR = "#607D8B"
    EDGE_WIDTH = 2

    def render(self, svg, model):

        #
        # Build node lookup
        #

        node_lookup = {
            node["id"]: node
            for node in model["nodes"]
        }

        #
        # Draw every edge
        #

        for edge in model["edges"]:

            source = node_lookup.get(edge["source"])
            target = node_lookup.get(edge["target"])

            if not source or not target:
                continue

            self.draw_edge(svg, source, target)

    def draw_edge(self, svg, source, target):

        #
        # Bottom center of source
        #

        x1 = source["x"] + source["width"] / 2
        y1 = source["y"] + source["height"]

        #
        # Top center of target
        #

        x2 = target["x"] + target["width"] / 2
        y2 = target["y"]

        #
        # Orthogonal routing
        #

        mid_y = (y1 + y2) / 2

        path = (
            f"M {x1} {y1} "
            f"L {x1} {mid_y} "
            f"L {x2} {mid_y} "
            f"L {x2} {y2}"
        )

        svg.append(f"""
<path
d="{path}"
fill="none"
stroke="{self.EDGE_COLOR}"
stroke-width="{self.EDGE_WIDTH}"
marker-end="url(#arrow)"/>
""")
