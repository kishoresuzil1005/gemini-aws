from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
from collections import defaultdict
from typing import List

class GraphIndexer:
    """Builds and maintains fast lookup indexes."""
    
    def __init__(self, repository: GraphRepository):
        self.repository = repository
        # Very simple in-memory indexes
        self._by_type = defaultdict(list)
        self._by_provider = defaultdict(list)
        
    def build_indexes(self):
        graph = self.repository.engine.get_underlying_graph()
        for node_id, data in graph.nodes(data=True):
            res_type = data.get("resource_type")
            prov = data.get("provider")
            if res_type:
                self._by_type[res_type].append(node_id)
            if prov:
                self._by_provider[prov].append(node_id)
                
    def find_by_type(self, resource_type: str) -> List[str]:
        return self._by_type.get(resource_type, []