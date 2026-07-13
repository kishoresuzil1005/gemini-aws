from app.services.diagram.orthogonal_router import OrthogonalRouter
from app.services.diagram.relationship_style_engine import RelationshipStyleEngine

class EdgeRenderer:
    """
    Responsible ONLY for rendering relationships between resources.

    Supports orthogonal routing.
    """

    def render(self, svg, model):

        router = OrthogonalRouter()
        
        # Ensure node_lookup exists in model if not already present
        if "node_lookup" not in model:
            model["node_lookup"] = {node["id"]: node for node in model["nodes"]}

        edges = router.route(model)

        print("========== EDGE RENDERER ==========")
        print("Routes returned :", len(edges))
        print("===================================")

        for edge in edges:

            p = edge["points"]

            style = RelationshipStyleEngine.get_style(
                edge["relationship"]
            )

            dash = ""

            if style.dasharray:
                dash = f'stroke-dasharray="{style.dasharray}"'

            svg.append(f"""
<path
d="M {p[0][0]} {p[0][1]}
L {p[1][0]} {p[1][1]}
L {p[2][0]} {p[2][1]}
L {p[3][0]} {p[3][1]}"
stroke="{style.stroke}"
stroke-width="{style.width}"
fill="none"
marker-end="url(#{style.arrow})"
opacity="{style.opacity}"
{dash}
/>
""")

            mx = (p[1][0] + p[2][0]) / 2
            my = (p[1][1] + p[2][1]) / 2

            svg.append(f"""
<text
x="{mx}"
y="{my-6}"
font-family="Arial"
font-size="10"
fill="{style.label_color}"
text-anchor="middle">
{edge["relationship"]}
</text>
""")