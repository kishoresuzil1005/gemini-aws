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

    #
    # Colors
    #

    AWS_ACCOUNT = "#FFFFFF"

    VPC = "#E8F1FE"

    AZ = "#F6F8FA"

    PUBLIC_SUBNET = "#FFF8E1"

    PRIVATE_SUBNET = "#F3E5F5"

    BORDER = "#90A4AE"

    TITLE = "#37474F"

    def render(self, svg, layout):

        canvas = layout["canvas"]

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
fill="{self.AWS_ACCOUNT}"
stroke="#607D8B"
stroke-width="2"/>
""")

        svg.append("""
<text
x="40"
y="55"
font-size="24"
font-family="Arial"
font-weight="bold">
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

        svg.append(f"""
<rect
x="{x}"
y="{y}"
width="{w}"
height="{h}"
rx="14"
fill="{self.VPC}"
stroke="{self.BORDER}"
stroke-width="2"/>
""")

        svg.append(f"""
<text
x="{x+15}"
y="{y+25}"
font-size="18"
font-family="Arial"
font-weight="bold">
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

        svg.append(f"""
<rect
x="{x}"
y="{y}"
width="{w}"
height="{h}"
rx="10"
fill="{self.AZ}"
stroke="{self.BORDER}"
stroke-dasharray="6,4"/>
""")

        svg.append(f"""
<text
x="{x+10}"
y="{y+20}"
font-size="15"
font-family="Arial"
font-weight="bold">
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

        color = (

            self.PUBLIC_SUBNET

            if public

            else

            self.PRIVATE_SUBNET

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
stroke="#B0BEC5"
stroke-width="1.5"/>
""")

        svg.append(f"""
<text
x="{x+10}"
y="{y+20}"
font-size="13"
font-family="Arial">
{title}
</text>
""")
