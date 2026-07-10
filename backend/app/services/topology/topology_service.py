import time
from app.services.ai.architecture_service import ArchitectureService
from collections import defaultdict
from app.models import ResourceDB
from app.services.topology.category_map import CATEGORY_MAP

class TopologyService:
    def __init__(self, db=None):
        self.db = db
        self.architecture_service = ArchitectureService()
        self._graph_cache = None
        self._last_refresh = 0

    def get_categories(self):
        resources = self.db.query(ResourceDB).all()
        counts = defaultdict(int)

        # Pre-initialize core categories to guarantee they are displayed
        default_categories = ["Compute", "Storage", "Database", "Network", "Security"]
        for cat in default_categories:
            counts[cat] = 0

        for r in resources:
            r_type_upper = (r.resource_type or "").upper()
            category = CATEGORY_MAP.get(r_type_upper, "Other")
            counts[category] += 1

        return [
            {
                "name": category,
                "count": count
            }
            for category, count in counts.items()
            if category != "Other" or count > 0
        ]

    def get_resources_by_category(self, category: str):
        resources = self.db.query(ResourceDB).all()
        result = []

        for r in resources:
            r_type_upper = (r.resource_type or "").upper()
            mapped = CATEGORY_MAP.get(r_type_upper, "Other")

            if mapped.lower() == category.lower():
                result.append({
                    "id": r.resource_id,
                    "type": r.resource_type,
                    "name": r.name or r.resource_id,
                    "region": r.region or "unknown",
                    "status": r.status or "unknown"
                })

        result.sort(key=lambda x: (x["type"], x["name"]))
        return result



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
