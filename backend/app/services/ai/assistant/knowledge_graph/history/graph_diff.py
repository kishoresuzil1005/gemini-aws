from app.services.ai.assistant.knowledge_graph.history.graph_snapshot import GraphSnapshot

class GraphDiff:
    """Calculates the difference between two graph snapshots (What changed?)."""
    
    def calculate_diff(self, snapshot_a: GraphSnapshot, snapshot_b: GraphSnapshot):
        pas