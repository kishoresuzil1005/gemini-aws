import base64
from pathlib import Path

from app.services.diagram.layout_engine import LayoutEngine


class SVGRenderer:

    def __init__(self):

        self.layout_engine = LayoutEngine()

    def image_to_base64(self, path: str):

        if not path:
            return None

        p = Path(path)

        if not p.exists():
            return None

        ext = p.suffix.lower()

        mime = "image/svg+xml"

        if ext == ".png":
            mime = "image/png"

        elif ext in [".jpg", ".jpeg"]:
            mime = "image/jpeg"

        elif ext == ".webp":
            mime = "image/webp"

        with open(path, "rb") as f:

            encoded = base64.b64encode(f.read()).decode()

        return f"data:{mime};base64,{encoded}"

    def render(self):

        layout = self.layout_engine.build()

        svg = []

        width = layout["canvas"]["width"]
        height = layout["canvas"]["height"]

        svg.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" '
            f'style="background:#f5f7fb">'
        )

        #
        # Draw Layers
        #

        for layer in layout["layers"]:

            svg.append(f'''
            <rect
                x="{layer["x"]}"
                y="{layer["y"]}"
                rx="15"
                ry="15"
                width="{layer["width"]}"
                height="{layer["height"]}"
                fill="#e9f3ff"
                stroke="#7eaee6"
                stroke-width="2"/>
            ''')

            svg.append(f'''
            <text
                x="{layer["x"]+15}"
                y="{layer["y"]+25}"
                font-size="20"
                font-family="Arial"
                font-weight="bold">
                {layer["name"]}
            </text>
            ''')

        #
        # Draw Resources
        #

        for layer in layout["layers"]:

            for node in layer["resources"]:

                image = self.image_to_base64(node.get("icon"))

                if image:

                    svg.append(f'''
                    <image
                        href="{image}"
                        x="{node["x"]}"
                        y="{node["y"]}"
                        width="{node["width"]}"
                        height="{node["height"]}"
                    />
                    ''')

                else:

                    svg.append(f'''
                    <rect
                        x="{node["x"]}"
                        y="{node["y"]}"
                        width="{node["width"]}"
                        height="{node["height"]}"
                        fill="#ffffff"
                        stroke="#333333"/>
                    ''')

                svg.append(f'''
                <text
                    x="{node["x"]}"
                    y="{node["y"]+110}"
                    font-size="12"
                    font-family="Arial">
                    {node["type"]}
                </text>
                ''')

        #
        # Draw Connections
        #

        node_lookup = {}

        for layer in layout["layers"]:

            for node in layer["resources"]:

                node_lookup[node["id"]] = node

        for edge in layout["edges"]:

            src = node_lookup.get(edge["source"])
            dst = node_lookup.get(edge["target"])

            if not src or not dst:
                continue

            x1 = src["x"] + 45
            y1 = src["y"] + 45

            x2 = dst["x"] + 45
            y2 = dst["y"] + 45

            svg.append(f'''
            <line
                x1="{x1}"
                y1="{y1}"
                x2="{x2}"
                y2="{y2}"
                stroke="#666666"
                stroke-width="2"
                marker-end="url(#arrow)"/>
            ''')

        #
        # Arrow Marker
        #

        svg.append("""
        <defs>

            <marker
                id="arrow"
                markerWidth="10"
                markerHeight="10"
                refX="10"
                refY="3"
                orient="auto">

                <path
                    d="M0,0 L10,3 L0,6"
                    fill="#666"/>

            </marker>

        </defs>
        """)

        svg.append("</svg>")

        return "\n".join(svg)
