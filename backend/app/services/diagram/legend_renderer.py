from app.services.diagram.theme_manager import ThemeManager
from app.services.diagram.typography_engine import TypographyEngine
from app.services.diagram.aws_color_palette import AWSColorPalette


class LegendRenderer:
    """
    Draws the legend panel for the architecture diagram.

    Shows:
    - AWS service colors
    - Relationship styles
    - Diagram statistics
    """

    WIDTH = 280

    PADDING = 16

    ROW_HEIGHT = 24

    SERVICES = [
        ("EC2", "Compute"),
        ("Lambda", "Serverless"),
        ("S3", "Storage"),
        ("RDS", "Database"),
        ("VPC", "Networking"),
        ("IAM", "Security"),
    ]

    RELATIONSHIPS = [
        ("────►", "Attached To"),
        ("- - -►", "In Subnet"),
        ("─ · ─►", "Uses Role"),
    ]

    def __init__(self):

        self.theme = ThemeManager()

    def render(self, svg: list, model: dict):

        canvas = model["canvas"]

        x = canvas["width"] - self.WIDTH - 30

        y = 30

        height = (
            110
            + len(self.SERVICES) * self.ROW_HEIGHT
            + len(self.RELATIONSHIPS) * self.ROW_HEIGHT
            + 70
        )

        #
        # Panel
        #

        svg.append(f"""
<rect
x="{x}"
y="{y}"
width="{self.WIDTH}"
height="{height}"
rx="12"
fill="#FFFFFF"
stroke="#CFD8DC"
stroke-width="2"/>
""")

        #
        # Title
        #

        svg.append(f"""
<text
x="{x+18}"
y="{y+28}"
font-family="Arial"
font-size="16"
font-weight="bold"
fill="#263238">
Legend
</text>
""")

        current_y = y + 60

        #
        # AWS Services
        #

        for service, _ in self.SERVICES:

            color = AWSColorPalette.get_fill(service)

            svg.append(f"""
<rect
x="{x+18}"
y="{current_y-10}"
width="12"
height="12"
fill="{color}"
stroke="#455A64"/>
""")

            svg.append(f"""
<text
x="{x+40}"
y="{current_y}"
font-family="Arial"
font-size="11"
fill="#263238">
{service}
</text>
""")

            current_y += self.ROW_HEIGHT

        #
        # Divider
        #

        current_y += 6

        svg.append(f"""
<line
x1="{x+10}"
y1="{current_y}"
x2="{x+self.WIDTH-10}"
y2="{current_y}"
stroke="#CFD8DC"/>
""")

        current_y += 24

        #
        # Relationships
        #

        for symbol, text in self.RELATIONSHIPS:

            svg.append(f"""
<text
x="{x+18}"
y="{current_y}"
font-family="Arial"
font-size="11">
{symbol}
</text>
""")

            svg.append(f"""
<text
x="{x+95}"
y="{current_y}"
font-family="Arial"
font-size="11"
fill="#263238">
{text}
</text>
""")

            current_y += self.ROW_HEIGHT

        #
        # Divider
        #

        current_y += 8

        svg.append(f"""
<line
x1="{x+10}"
y1="{current_y}"
x2="{x+self.WIDTH-10}"
y2="{current_y}"
stroke="#CFD8DC"/>
""")

        current_y += 24

        #
        # Statistics
        #

        svg.append(f"""
<text
x="{x+18}"
y="{current_y}"
font-family="Arial"
font-size="11"
fill="#263238">
Resources : {len(model["nodes"])}
</text>
""")

        current_y += 20

        svg.append(f"""
<text
x="{x+18}"
y="{current_y}"
font-family="Arial"
font-size="11"
fill="#263238">
Relationships : {len(model["edges"])}
</text>
"""