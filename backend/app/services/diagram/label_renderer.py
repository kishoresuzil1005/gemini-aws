class LabelRenderer:
    """
    Responsible ONLY for rendering text labels.

    It renders:

    - Display name
    - Resource ID
    - Resource state
    - Instance type
    """

    TITLE_SIZE = 14
    META_SIZE = 11

    TITLE_COLOR = "#263238"
    META_COLOR = "#607D8B"

    def render(self, svg, nodes):

        for node in nodes:

            self.render_node(svg, node)

    def render_node(self, svg, node):

        x = node["x"]
        y = node["y"]

        metadata = node.get("metadata", {})

        #
        # Display Name
        #

        display = (

            node.get("display_name")

            or node.get("name")

            or node["type"]

        )

        svg.append(f"""
<text
x="{x+60}"
y="{y+26}"
font-size="{self.TITLE_SIZE}"
font-family="Arial"
font-weight="bold"
fill="{self.TITLE_COLOR}">
{display}
</text>
""")

        #
        # Resource ID
        #

        resource_id = node.get("id")

        if resource_id:

            svg.append(f"""
<text
x="{x+60}"
y="{y+44}"
font-size="{self.META_SIZE}"
font-family="Arial"
fill="{self.META_COLOR}">
{resource_id}
</text>
""")

        #
        # State
        #

        state = (

            metadata.get("state")

            or metadata.get("status")

            or metadata.get("State")

        )

        if state:

            svg.append(f"""
<text
x="{x+60}"
y="{y+60}"
font-size="{self.META_SIZE}"
font-family="Arial"
fill="{self.META_COLOR}">
{state}
</text>
""")

        #
        # Instance Type
        #

        instance_type = (

            metadata.get("instance_type")

            or metadata.get("InstanceType")

        )

        if instance_type:

            svg.append(f"""
<text
x="{x+60}"
y="{y+76}"
font-size="{self.META_SIZE}"
font-family="Arial"
fill="{self.META_COLOR}">
{instance_type}
</text>
""")
