from app.services.diagram.theme_manager import ThemeManager
from app.services.diagram.typography_engine import TypographyEngine


class ContainerRenderer:
    """
    Enterprise Container Renderer

    Draws:

    - AWS Account
    - VPC
    - Availability Zone
    - Public Subnet
    - Private Subnet

    Never draws:

    - EC2
    - Lambda
    - Icons
    - Relationships
    """

    ACCOUNT_PADDING = 20
    HEADER_HEIGHT = 40

    def __init__(self):

        self.theme = ThemeManager()

    def render(self, svg, model):

        self.render_account(svg, model)

        for vpc in model.get("vpcs", []):

            self.render_vpc(svg, vpc)

            for az in vpc.get("availability_zones", []):

                self.render_availability_zone(svg, az)

                for subnet in az.get("public_subnets", []):

                    self.render_public_subnet(svg, subnet)

                for subnet in az.get("private_subnets", []):

                    self.render_private_subnet(svg, subnet)

    ####################################################################
    # AWS ACCOUNT
    ####################################################################

    def render_account(self, svg, model):

        canvas = model["canvas"]

        style = TypographyEngine.ACCOUNT

        svg.append(f"""
<rect
x="20"
y="20"
width="{canvas['width']-40}"
height="{canvas['height']-40}"
rx="16"
fill="{self.theme.account.fill}"
stroke="{self.theme.account.border}"
stroke-width="2"/>
""")

        svg.append(f"""
<text
x="40"
y="55"
font-family="{style.family}"
font-size="{style.size}"
font-weight="{style.weight}"
fill="{style.color}">
AWS Account
</text>
""")

    ####################################################################
    # VPC
    ####################################################################

    def render_vpc(self, svg, vpc):

        style = TypographyEngine.VPC

        svg.append(f"""
<rect
x="{vpc['x']}"
y="{vpc['y']}"
width="{vpc['width']}"
height="{vpc['height']}"
rx="14"
fill="{self.theme.vpc.fill}"
stroke="{self.theme.vpc.border}"
stroke-width="2"/>
""")

        svg.append(f"""
<rect
x="{vpc['x']}"
y="{vpc['y']}"
width="{vpc['width']}"
height="{self.HEADER_HEIGHT}"
rx="14"
fill="{self.theme.vpc.border}"/>
""")

        svg.append(f"""
<text
x="{vpc['x']+18}"
y="{vpc['y']+27}"
font-family="{style.family}"
font-size="{style.size}"
font-weight="{style.weight}"
fill="#FFFFFF">
{TypographyEngine.truncate(vpc['name'])}
</text>
""")

    ####################################################################
    # AVAILABILITY ZONE
    ####################################################################

    def render_availability_zone(self, svg, az):

        style = TypographyEngine.AZ

        svg.append(f"""
<rect
x="{az['x']}"
y="{az['y']}"
width="{az['width']}"
height="{az['height']}"
rx="12"
fill="{self.theme.az.fill}"
stroke="{self.theme.az.border}"
stroke-width="1.5"/>
""")

        svg.append(f"""
<rect
x="{az['x']}"
y="{az['y']}"
width="{az['width']}"
height="34"
rx="12"
fill="#CFD8DC"/>
""")

        svg.append(f"""
<text
x="{az['x']+15}"
y="{az['y']+22}"
font-family="{style.family}"
font-size="{style.size}"
font-weight="{style.weight}"
fill="{style.color}">
{TypographyEngine.truncate(az['name'])}
</text>
""")

    ####################################################################
    # PUBLIC SUBNET
    ####################################################################

    def render_public_subnet(self, svg, subnet):

        svg.append(f"""
<rect
x="{subnet['x']}"
y="{subnet['y']}"
width="{subnet['width']}"
height="{subnet['height']}"
rx="10"
fill="{self.theme.subnet.public_fill}"
stroke="#64B5F6"
stroke-width="1.5"/>
""")

    ####################################################################
    # PRIVATE SUBNET
    ####################################################################

    def render_private_subnet(self, svg, subnet):

        svg.append(f"""
<rect
x="{subnet['x']}"
y="{subnet['y']}"
width="{subnet['width']}"
height="{subnet['height']}"
rx="10"
fill="{self.theme.subnet.private_fill}"
stroke="#B0BEC5"
stroke-width="1.5"/>
"""