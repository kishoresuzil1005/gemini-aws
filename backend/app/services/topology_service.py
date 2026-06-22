import time
from app.services.architecture_service import ArchitectureService


class TopologyService:

    def __init__(self):
        self.architecture_service = ArchitectureService()
        self._graph_cache = None
        self._last_refresh = 0

    def _get_graph(self):
        now = time.time()

        if (
            self._graph_cache
            is not None
            and now - self._last_refresh < 300
        ):
            return self._graph_cache

        try:
            graph = self.architecture_service.build_graph()

            if not graph:
                self._graph_cache = {"nodes": [], "edges": []}
            else:
                self._graph_cache = {
                    "nodes": graph.get("nodes", []),
                    "edges": graph.get("edges", [])
                }

            self._last_refresh = now
            return self._graph_cache

        except Exception as e:
            print(f"[TOPOLOGY ERROR] {e}")
            return {
                "nodes": [],
                "edges": []
            }

    def get_graph(self):
        graph = self._get_graph()

        return {
            "success": True,
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "nodes": graph["nodes"],
            "edges": graph["edges"]
        }

    def get_nodes(self):
        graph = self._get_graph()
        return graph["nodes"]

    def get_edges(self):
        graph = self._get_graph()
        return graph["edges"]

    def get_resource(self, resource_id):
        graph = self._get_graph()

        node = next(
            (n for n in graph["nodes"] if n["id"] == resource_id),
            None
        )

        if not node:
            return {
                "success": False,
                "message": "Resource not found"
            }

        dependencies = [
            e for e in graph["edges"]
            if e["source"] == resource_id
        ]

        return {
            "success": True,
            "resource": node,
            "dependencies": dependencies
        }

    def blast_radius(self, resource_id):
        graph = self._get_graph()

        affected = [
            e["source"]
            for e in graph["edges"]
            if e["target"] == resource_id
        ]

        return {
            "success": True,
            "resource": resource_id,
            "affected_resources": affected,
            "count": len(affected)
        }
