import base64
from pathlib import Path


class IconRenderer:
    """
    Responsible ONLY for rendering AWS SVG icons.
    """

    ICON_SIZE = 42

    def __init__(self):

        self.cache = {}

    def image_to_base64(self, path):

        if path in self.cache:
            return self.cache[path]

        p = Path(path)

        if not p.exists():
            return None

        with open(p, "rb") as f:

            encoded = base64.b64encode(
                f.read()
            ).decode()

        self.cache[path] = encoded

        return encoded

    def render(self, svg, nodes):

        for node in nodes:

            icon = node.get("icon")

            if not icon:
                continue

            encoded = self.image_to_base64(icon)

            if not encoded:
                continue

            x = node["x"] + 12

            y = node["y"] + 10

            svg.append(f"""
<image
x="{x}"
y="{y}"
width="{self.ICON_SIZE}"
height="{self.ICON_SIZE}"
href="data:image/svg+xml;base64,{encoded}" />
""")
