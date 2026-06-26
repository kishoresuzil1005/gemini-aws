from app.services.diagram.smart_layout_engine import SmartLayoutEngine

from app.services.diagram.background_renderer import (
    BackgroundRenderer
)

from app.services.diagram.container_renderer import (
    ContainerRenderer
)

from app.services.diagram.edge_renderer import (
    EdgeRenderer
)

from app.services.diagram.icon_renderer import (
    IconRenderer
)

from app.services.diagram.label_renderer import (
    LabelRenderer
)

from app.services.diagram.node_renderer import (
    NodeRenderer
)

from app.services.diagram.legend_renderer import (
    LegendRenderer
)


class SVGRenderer:
    """
    Main SVG Composer.

    Coordinates all renderers.
    """

    def __init__(self):

        self.layout = SmartLayoutEngine()

        self.background = BackgroundRenderer()

        self.container = ContainerRenderer()

        self.edges = EdgeRenderer()

        self.icons = IconRenderer()

        self.labels = LabelRenderer()

        self.node_renderer = NodeRenderer()

        self.legend = LegendRenderer()

    def render(self):

        model = self.layout.build()

        print("========== SVG RENDERER ==========")
        print("Nodes :", len(model["nodes"]))
        print("Edges :", len(model["edges"]))
        print("==================================")

        svg = []

        width = model["canvas"]["width"]

        height = model["canvas"]["height"]

        #
        # SVG Header
        #

        svg.append(f"""
<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}">
""")

        #
        # Arrow Definition
        #

        svg.append("""
<defs>

<marker
id="arrow"
markerWidth="12"
markerHeight="12"
refX="10"
refY="4"
orient="auto"
markerUnits="strokeWidth">

<path
d="M0,0 L0,8 L10,4 z"
fill="#607D8B"/>

</marker>

</defs>
""")

        #
        # Background
        #

        self.background.render(

            svg,

            model

        )

        #
        # Infrastructure Containers
        #

        self.container.render(

            svg,

            model

        )

        #
        # Node Cards
        #

        self.node_renderer.render(

            svg,

            model["nodes"]

        )

        #
        # Relationships
        #

        self.edges.render(

            svg,

            model

        )

        #
        # AWS Icons
        #

        self.icons.render(

            svg,

            model["nodes"]

        )

        #
        # Labels
        #

        self.labels.render(

            svg,

            model["nodes"]

        )

        #
        # Legend
        #

        self.legend.render(
            svg,
            model
        )

        #
        # Close SVG
        #

        svg.append("</svg>")

        return "\n".join(svg)
