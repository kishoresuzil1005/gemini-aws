from app.services.architecture_service import ArchitectureService


class TopologyService:

    def __init__(self):
        self.architecture_service = ArchitectureService()

    def _get_graph(self):

        graph = self.architecture_service.build_graph()

        if not graph:
            return {
                "nodes": [],
                "edges": []
            }

        if isinstance(graph, list):
            return {
                "nodes": graph,
                "edges": []
            }

        return graph

    def get_graph(self):

        graph = self._get_graph()

        return {
            "success": True,
            "node_count": len(graph.get("nodes", [])),
            "edge_count": len(graph.get("edges", [])),
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", [])
        }

    def get_nodes(self):

        graph = self._get_graph()

        return {
            "success": True,
            "count": len(graph.get("nodes", [])),
            "nodes": graph.get("nodes", [])
        }

    def get_edges(self):

        graph = self._get_graph()

        return {
            "success": True,
            "count": len(graph.get("edges", [])),
            "edges": graph.get("edges", [])
        }

    def get_resource(self, resource_id):

        graph = self._get_graph()

        for node in graph.get("nodes", []):

            if node.get("id") == resource_id:

                dependencies = []

                for edge in graph.get("edges", []):

                    if edge.get("source") == resource_id:
                        dependencies.append(edge.get("target"))

                return {
                    "success": True,
                    "resource": node,
                    "dependencies": dependencies
                }

        return {
            "success": False,
            "message": "Resource not found"
        }

    def blast_radius(self, resource_id):

        graph = self._get_graph()

        affected = []

        for edge in graph.get("edges", []):

            if edge.get("target") == resource_id:
                affected.append(edge.get("source"))

        return {
            "success": True,
            "resource": resource_id,
            "affected_resources": affected,
            "count": len(affected)
        }
