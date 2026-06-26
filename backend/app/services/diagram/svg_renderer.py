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
markerWidth="10"
markerHeight="10"
refX="8"
refY="3"
orient="auto">

<path
d="M0,0 L0,6 L9,3 z"
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
        # Close SVG
        #

        svg.append("</svg>")

        return "\n".join(svg)
