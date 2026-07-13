from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
from app.services.ai.assistant.knowledge_graph.core.graph_indexer import GraphIndexer
from typing import List, Optional
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode

class GraphSearchEngine:
    """Google-like search for infrastructure nodes."""
    
    def __init__(self, repository: GraphRepository, indexer: GraphIndexer):
        self.repository = repository
        self.indexer = indexer
        
    def search_by_type(self, resource_type: str) -> List[CloudNode]:
        node_ids = self.indexer.find_by_type(resource_type)
        return [self.repository.find_node(nid) for nid in node_ids if self.repository.find_node(nid)]