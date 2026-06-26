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

        for node in nodes:

            icon_svg = SVGIconCache.get(node["type"])

            #
            # Unknown resource
            #

            if not icon_svg:
                continue

            #
            # Center icon
            #

            x = (
                node["x"]
                + (node["width"] - self.ICON_SIZE) / 2
            )

            y = (
                node["y"]
                + 12
            )

            transformed = SVGTransformEngine.transform(
                svg_fragment=icon_svg,
                x=x,
                y=y,
                size=self.ICON_SIZE
            )

            svg.append(transformed)
