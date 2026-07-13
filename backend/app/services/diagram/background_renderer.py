from app.services.diagram.theme_manager import ThemeManager

class BackgroundRenderer:
    """
    Responsible ONLY for drawing
    the SVG background.
    """

    def render(self, svg, model):

        width = model["canvas"]["width"]
        height = model["canvas"]["height"]
        
        theme = ThemeManager()

        svg.append(f"""
<rect
width="{width}"
height="{height}"
fill="{theme.canvas.background}"/>
""")