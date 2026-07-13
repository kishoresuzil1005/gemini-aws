from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
import networkx as nx

class GraphTraversal:
    """Advanced algorithms using NetworkX internally."""
    
    def __init__(self, repository: GraphRepository):
        self.repository = repository
        
    def get_shortest_path(self, source_id: str, target_id: str):
        graph = self.repository.engine.get_underlying_graph()
        try:
            return nx.shortest_path(graph, source=source_id, target=target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
            
    def get_blast_radius_subgraph(self, node_id: str, max_depth: int = 3):
        """Returns all nodes reachable from the target node up to a certain depth."""
        graph = self.repository.engine.get_underlying_graph()
        if not graph.has_node(node_id):
            return []
            
        # BFS tree
        edges = nx.bfs_edges(graph, node_id, depth_limit=max_depth)
        nodes = set([node_id])
        for u, v in edges:
            nodes.add(u)
            nodes.add(v)
            
        return list(nodes)