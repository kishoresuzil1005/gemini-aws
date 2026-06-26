from app.services.diagram.theme_manager import ThemeManager
from app.services.diagram.typography_engine import TypographyEngine
from app.services.diagram.aws_color_palette import AWSColorPalette


class NodeRenderer:

    CARD_WIDTH = 180
    CARD_HEIGHT = 120

    ICON_SIZE = 48

    def __init__(self):

        self.theme = ThemeManager()

    def render(self, svg, nodes):

        for node in nodes:

            self.draw_card(svg, node)

            self.draw_title(svg, node)

            self.draw_metadata(svg, node)

    ##################################################

    def draw_card(self, svg, node):

        color = AWSColorPalette.get_border(node["type"])

        svg.append(f"""
<rect
x="{node['x']}"
y="{node['y']}"
width="{self.CARD_WIDTH}"
height="{self.CARD_HEIGHT}"
rx="12"
fill="{self.theme.node.fill}"
stroke="{color}"
stroke-width="2"/>
""")

    ##################################################

    def draw_title(self, svg, node):

        style = TypographyEngine.NODE

        title = TypographyEngine.truncate(

            node.get("display_name","")

        )

        svg.append(f"""
<text
x="{node['x']+16}"
y="{node['y']+82}"
font-family="{style.family}"
font-size="{style.size}"
font-weight="{style.weight}"
fill="{style.color}">
{title}
</text>
""")

    ##################################################

    def draw_metadata(self, svg, node):

        style = TypographyEngine.METADATA

        meta = node.get("type","")

        svg.append(f"""
<text
x="{node['x']+16}"
y="{node['y']+102}"
font-family="{style.family}"
font-size="{style.size}"
fill="{style.color}">
{meta}
</text>
""")
