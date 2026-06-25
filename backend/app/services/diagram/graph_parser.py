from app.services.graph.neo4j_service import Neo4jService


class GraphParser:

    def parse(self):

        service = Neo4jService()

        try:

            res = service.get_graph()

            nodes = []

            for n in res.get("nodes", []):

                nodes.append({

                    "id": n["id"],

                    "type": n["type"]

                })

            edges = []

            for e in res.get("edges", []):

                edges.append({

                    "source": e["source"],

                    "target": e["target"],

                    "relationship": e.get("relation") or e.get("relationship") or "RELATED_TO"

                })

            return {

                "nodes": nodes,

                "edges": edges

            }

        finally:

            service.close()
