from app.services.diagram.typography_engine import TypographyEngine

class LabelRenderer:
    """
    Responsible ONLY for rendering text labels.

    It renders:

    - Display name
    - Resource ID
    - Resource state
    - Instance type
    """

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
        name_style = TypographyEngine.NODE
        name = TypographyEngine.truncate(name, 28)

        svg.append(f"""
<text
x="{layout['title_x']}"
y="{layout['title_y']}"
text-anchor="middle"
font-size="{name_style.size}"
font-family="{name_style.family}"
font-weight="{name_style.weight}"
fill="{name_style.color}">
{name}
</text>
""")

        #
        # Resource ID
        #

        resource_id = node.get("id", "")

        # Draw the ID only if it's different
        if resource_id and resource_id != name:
            
            meta_style = TypographyEngine.METADATA
            short_id = TypographyEngine.truncate(resource_id, 24)

            svg.append(f"""
<text
x="{layout['subtitle_x']}"
y="{layout['subtitle_y']}"
text-anchor="middle"
font-size="{meta_style.size}"
font-family="{meta_style.family}"
font-weight="{meta_style.weight}"
fill="{meta_style.color}">
{short_id}
</text>
""")
