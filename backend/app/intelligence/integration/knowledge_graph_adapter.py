from typing import Dict, Any

class KnowledgeGraphAdapter:
    """
    Acts as the integration layer between the Intelligence platform and the existing Knowledge Graph.
    Transforms graph traversal results into flat metrics for analytics.
    """
    def fetch_blast_radius(self, resource_id: str) -> Dict[str, Any]:
        print(f"[KnowledgeGraphAdapter] Querying Knowledge Graph for {resource_id} blast radius...")
        # Mocking an adapter translation
        return {"affected_nodes": 12, "critical_path": True}
