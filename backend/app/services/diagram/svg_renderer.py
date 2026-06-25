import base64
from pathlib import Path

from app.services.diagram.layout_engine import LayoutEngine


class SVGRenderer:
    """
    Renders a professional AWS Architecture Diagram as SVG.
    """

    BACKGROUND = "#F8FAFC"
    NODE_FILL = "#FFFFFF"
    NODE_BORDER = "#CBD5E1"
    LAYER_FILL = "#F1F5F9"
    LAYER_BORDER = "#94A3B8"
    TEXT_COLOR = "#1E293B"

    def __init__(self):
        self.layout = LayoutEngine()

    def image_to_base64(self, path):

        if not Path(path).exists():
            return None

        with open(path, "rb") as f:
            return base64.b64encode(
                f.read()
            ).decode()

    def render(self):

        model = self.layout.build()

        svg = []

        width = model["canvas"]["width"]
        height = model["canvas"]["height"]

        svg.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}">'
        )

        #
        # Background
        #

        svg.append(
            f'<rect width="{width}" height="{height}" '
            f'fill="{self.BACKGROUND}"/>'
        )

        #
        # Draw Edges
        #

        for edge in model["edges"]:

            source = next(
                (
                    n
                    for n in model["nodes"]
                    if n["type"] == edge["source"]
                ),
                None
            )

            target = next(
                (
                    n
                    for n in model["nodes"]
                    if n["type"] == edge["target"]
                ),
                None
            )

            if not source or not target:
                continue

            x1 = source["x"] + source["width"] / 2
            y1 = source["y"] + source["height"]

            x2 = target["x"] + target["width"] / 2
            y2 = target["y"]

            svg.append(
                f'<line x1="{x1}" y1="{y1}" '
                f'x2="{x2}" y2="{y2}" '
                f'stroke="#64748B" stroke-width="2"/>'
            )

        #
        # Draw Nodes
        #

        for node in model["nodes"]:

            x = node["x"]
            y = node["y"]
            w = node["width"]
            h = node["height"]

            svg.append(
                f'<rect x="{x}" y="{y}" '
                f'width="{w}" height="{h}" '
                f'rx="10" ry="10" '
                f'fill="{self.NODE_FILL}" '
                f'stroke="{self.NODE_BORDER}" '
                f'stroke-width="2"/>'
            )

            icon_data = self.image_to_base64(
                node["icon"]
            )

            if icon_data:

                svg.append(
                    f'<image '
                    f'x="{x+10}" '
                    f'y="{y+12}" '
                    f'width="32" '
                    f'height="32" '
                    f'href="data:image/svg+xml;base64,{icon_data}"/>'
                )

            svg.append(
                f'<text '
                f'x="{x+50}" '
                f'y="{y+34}" '
                f'font-size="14" '
                f'font-family="Arial" '
                f'fill="{self.TEXT_COLOR}">'
                f'{node["display_name"]}'
                f'</text>'
            )

        svg.append("</svg>")

        return "\n".join(svg)
