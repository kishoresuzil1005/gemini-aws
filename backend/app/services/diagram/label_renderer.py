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

        from app.services.diagram.node_layout_engine import NodeLayoutEngine

        layout = NodeLayoutEngine.build(node)

        #
        # Display Name
        #

        name = (
            node.get("display_name")
            or node.get("name")
            or node.get("id")
        )

        svg.append(f"""
<text
x="{layout['title_x']}"
y="{layout['title_y']}"
text-anchor="middle"
font-size="{self.TITLE_SIZE}"
font-family="Arial"
font-weight="bold"
fill="{self.TITLE_COLOR}">
{name}
</text>
""")

        #
        # Resource ID
        #

        resource_id = node.get("id", "")

        # Draw the ID only if it's different
        if resource_id and resource_id != name:
            
            def shorten(text, limit=24):
                if len(text) <= limit:
                    return text
                return text[:21] + "..."
                
            short_id = shorten(resource_id)

            svg.append(f"""
<text
x="{layout['subtitle_x']}"
y="{layout['subtitle_y']}"
text-anchor="middle"
font-size="{self.META_SIZE}"
font-family="Arial"
fill="{self.META_COLOR}">
{short_id}
</text>
""")
