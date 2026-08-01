from app.core.logging import get_logger
logger = get_logger(__name__)
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

        logger.debug("========== ORTHOGONAL ROUTER ==========")
        logger.debug(f"Graph edges : {len(graph['edges'])}")
        logger.debug(f"Node lookup : {len(graph['node_lookup'])}")

        node_lookup = graph["node_lookup"]

        routed_edges = []

        for edge in graph["edges"]:

            source = node_lookup.get(edge["source"])
            target = node_lookup.get(edge["target"])

            if not source:
                logger.debug(f"Missing source node: {edge['source']}")
                continue

            if not target:
                logger.debug(f"Missing target node: {edge['target']}")
                continue

            #
            # Node centers (use .get() with defaults to avoid KeyError on missing layout data)
            #
            src_x = source.get("x", 0)
            src_y = source.get("y", 0)
            src_w = source.get("width", 120)
            src_h = source.get("height", 60)

            tgt_x = target.get("x", 0)
            tgt_y = target.get("y", 0)
            tgt_w = target.get("width", 120)
            tgt_h = target.get("height", 60)

            sx = src_x + src_w / 2
            sy = src_y + src_h / 2

            tx = tgt_x + tgt_w / 2
            ty = tgt_y + tgt_h / 2

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

        logger.debug(f"Routes created : {len(routed_edges)}")
        logger.debug("======================================")

        return routed_edges