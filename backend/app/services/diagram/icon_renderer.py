from app.services.diagram.svg_icon_cache import SVGIconCache
from app.services.diagram.svg_transform_engine import SVGTransformEngine


class IconRenderer:
    """
    Renders AWS icons into the final SVG.

    Responsibilities
    ----------------
    - Fetch icon from cache
    - Position icon
    - Embed SVG

    Does NOT
    --------
    - Load icons
    - Cache icons
    - Sanitize SVG
    """

    ICON_SIZE = 48

    def render(self, svg: list, nodes: list):

        from app.services.diagram.node_layout_engine import NodeLayoutEngine

        for node in nodes:

            icon_svg = SVGIconCache.get(node["type"])

            #
            # Unknown resource
            #

            if not icon_svg:
                continue

            layout = NodeLayoutEngine.build(node)

            transformed = SVGTransformEngine.transform(
                svg_fragment=icon_svg,
                x=layout["icon_x"],
                y=layout["icon_y"],
                size=self.ICON_SIZE
            )

            svg.append(transformed)
