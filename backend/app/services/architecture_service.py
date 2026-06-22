from app.services.ai.account_tree_service import AccountTreeService

class ArchitectureService:

    def __init__(self):
        self.tree_service = AccountTreeService()

    def build_graph(self):
        nodes = []
        edges = []

        try:
            res = self.tree_service.generate_tree()
            if isinstance(res, dict):
                nodes = res.get("nodes", [])
                edges = res.get("edges", [])
        except Exception as e:
            print(f"[TOPOLOGY] Error generating tree: {e}")

        graph = {
            "nodes": nodes,
            "edges": edges
        }

        print(
            f"[TOPOLOGY] Generated "
            f"{len(nodes)} nodes and "
            f"{len(edges)} edges"
        )

        return graph
