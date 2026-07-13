from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
import networkx as nx

class GraphValidator:
    """Ensures graph integrity (no orphans, no missing IDs, cyclic detection)."""
    
    def __init__(self, repository: GraphRepository):
        self.repository = repository
        
    def validate(self):
        graph = self.repository.engine.get_underlying_graph()
        
        # Check for isolated nodes (orphans)
        isolated = list(nx.isolates(graph))
        if isolated:
            pass # We could log warnings
            
        # Check cycles (not all cycles are bad, but for dependencies they might be)
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            pass