from app.services.architecture_service import ArchitectureService


class TopologyService:

    def __init__(self):
        self.arch = ArchitectureService()

    def get_graph(self):

        graph = self.arch.build_graph()

        return {
            "success": True,
            "nodes": graph["nodes"],
            "edges": graph["edges"]
        }

    def get_nodes(self):

        graph = self.arch.build_graph()

        return {
            "success": True,
            "count": len(graph["nodes"]),
            "nodes": graph["nodes"]
        }

    def get_edges(self):

        graph = self.arch.build_graph()

        return {
            "success": True,
            "count": len(graph["edges"]),
            "edges": graph["edges"]
        }

    def get_resource(self, resource_id):

        graph = self.arch.build_graph()

        for node in graph["nodes"]:

            if node["id"] == resource_id:

                dependencies = []

                for edge in graph["edges"]:

                    if edge["source"] == resource_id:

                        dependencies.append(edge["target"])

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

        graph = self.arch.build_graph()

        affected = []

        for edge in graph["edges"]:

            if edge["source"] == resource_id:

                affected.append(edge["target"])

        return {
            "success": True,
            "resource": resource_id,
            "affected_resources": affected,
            "count": len(affected)
        }
