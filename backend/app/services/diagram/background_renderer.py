class BackgroundRenderer:
    """
    Responsible ONLY for drawing
    the SVG background.
    """

    BACKGROUND = "#F8FAFC"

    def render(self, svg, model):

        width = model["canvas"]["width"]

        height = model["canvas"]["height"]

        svg.append(f"""
<rect
width="{width}"
height="{height}"
fill="{self.BACKGROUND}"/>
""")
