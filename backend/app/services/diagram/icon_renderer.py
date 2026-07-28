from app.core.logging import get_logger
logger = get_logger(__name__)
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

        logger.debug("========== ICON RENDERER ==========")
        logger.debug(f"Nodes received: {len(nodes)}")

        for node in nodes:

            icon_svg = SVGIconCache.get(node["type"])

            logger.debug(f"{node["type"]} -> {"FOUND" if icon_svg else "MISSING"}")

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

            logger.debug(f"Embedded: {node["type"]}")

            svg.append(transformed)