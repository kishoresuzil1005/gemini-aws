class OrthogonalRouter:
    """
    Computes right-angle (orthogonal) routes between nodes.

    Input:
        graph
        node positions

    Output:
        edges with path points
    """

    def route(self, graph: dict):

        print("========== ORTHOGONAL ROUTER ==========")
        print("Graph edges :", len(graph["edges"]))
        print("Node lookup :", len(graph["node_lookup"]))

        node_lookup = graph["node_lookup"]

        routed_edges = []

        for edge in graph["edges"]:

            source = node_lookup.get(edge["source"])
            target = node_lookup.get(edge["target"])

            if not source:
                print(f"Missing source node: {edge['source']}")
                continue

            if not target:
                print(f"Missing target node: {edge['target']}")
                continue

            #
            # Node centers
            #

            sx = source["x"] + source["width"] / 2
            sy = source["y"] + source["height"] / 2

            tx = target["x"] + target["width"] / 2
            ty = target["y"] + target["height"] / 2

            #
            # Midpoint
            #

            mx = sx
            my = ty

            routed_edges.append({

                "source": edge["source"],

                "target": edge["target"],

                "relationship": edge["relationship"],

                "points": [

                    (sx, sy),

                    (mx, sy),

                    (mx, my),

                    (tx, ty)

                ]

            })

        print("Routes created :", len(routed_edges))
        print("======================================")

        return routed_edge