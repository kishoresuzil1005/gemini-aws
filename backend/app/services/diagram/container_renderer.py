from app.services.diagram.theme_manager import ThemeManager
from app.services.diagram.typography_engine import TypographyEngine

class ContainerRenderer:
    """
    Responsible ONLY for drawing infrastructure containers.

    It does NOT render:

    - resources
    - icons
    - labels
    - edges

    It only draws:

    AWS Account
    VPC
    Availability Zones
    Public / Private Subnets
    """

    def render(self, svg, layout):

        canvas = layout["canvas"]

        theme = ThemeManager()
        style = TypographyEngine.ACCOUNT

        #
        # AWS Account
        #

        svg.append(f"""
<rect
x="20"
y="20"
width="{canvas['width']-40}"
height="{canvas['height']-40}"
rx="16"
fill="{theme.account.fill}"
stroke="{theme.account.border}"
stroke-width="2"/>
""")

        svg.append(f"""
<text
x="40"
y="55"
font-size="{style.size}"
font-family="{style.family}"
font-weight="{style.weight}"
fill="{style.color}">
AWS Account
</text>
""")

        #
        # VPC Containers
        #

        for vpc in layout.get("vpcs", []):

            self.render_vpc(svg, vpc)

    def render_vpc(self, svg, vpc):

        x = vpc["x"]

        y = vpc["y"]

        w = vpc["width"]

        h = vpc["height"]

        theme = ThemeManager()
        style = TypographyEngine.VPC

        svg.append(f"""
<rect
x="{x}"
y="{y}"
width="{w}"
height="{h}"
rx="14"
fill="{theme.vpc.fill}"
stroke="{theme.vpc.border}"
stroke-width="2"/>
""")

        svg.append(f"""
<text
x="{x+15}"
y="{y+25}"
font-size="{style.size}"
font-family="{style.family}"
font-weight="{style.weight}"
fill="{style.color}">
{vpc["name"]}
</text>
""")

        #
        # Availability Zones
        #

        for az in vpc.get("availability_zones", []):

            self.render_az(svg, az)

    def render_az(self, svg, az):

        x = az["x"]

        y = az["y"]

        w = az["width"]

        h = az["height"]

        theme = ThemeManager()
        style = TypographyEngine.AZ

        svg.append(f"""
<rect
x="{x}"
y="{y}"
width="{w}"
height="{h}"
rx="10"
fill="{theme.az.fill}"
stroke="{theme.az.border}"
stroke-dasharray="6,4"/>
""")

        svg.append(f"""
<text
x="{x+10}"
y="{y+20}"
font-size="{style.size}"
font-family="{style.family}"
font-weight="{style.weight}"
fill="{style.color}">
{az["name"]}
</text>
""")

        #
        # Public Subnets
        #

        for subnet in az.get("public_subnets", []):

            self.render_subnet(

                svg,

                subnet,

                public=True

            )

        #
        # Private Subnets
        #

        for subnet in az.get("private_subnets", []):

            self.render_subnet(

                svg,

                subnet,

                public=False

            )

    def render_subnet(

        self,

        svg,

        subnet,

        public

    ):

        theme = ThemeManager()
        style = TypographyEngine.METADATA
        
        color = (
            theme.subnet.public_fill
            if public
            else
            theme.subnet.private_fill
        )

        title = (
            "Public Subnet"
            if public
            else
            "Private Subnet"
        )

        x = subnet["x"]

        y = subnet["y"]

        w = subnet["width"]

        h = subnet["height"]

        svg.append(f"""
<rect
x="{x}"
y="{y}"
width="{w}"
height="{h}"
rx="8"
fill="{color}"
stroke="{theme.subnet.border}"
stroke-width="1.5"/>
""")

        svg.append(f"""
<text
x="{x+10}"
y="{y+20}"
font-size="{style.size}"
font-family="{style.family}"
font-weight="{style.weight}"
fill="{style.color}">
{title}
</text>
""")
