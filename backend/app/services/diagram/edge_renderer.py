from app.services.diagram.orthogonal_router import OrthogonalRouter

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

        print("================================")
        print("EDGE RENDERER")
        print("Edges received :", len(edges))
        print("================================")

        for edge in edges:

            p = edge["points"]

            svg.append(f'''
<path
d="M {p[0][0]} {p[0][1]}
L {p[1][0]} {p[1][1]}
L {p[2][0]} {p[2][1]}
L {p[3][0]} {p[3][1]}"
stroke="#64748B"
stroke-width="2"
fill="none"
marker-end="url(#arrow)"
/>
''')
