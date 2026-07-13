from typing import List
from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository

class ServiceMapEngine:
    """Builds logical application maps from infrastructure components."""
    
    def __init__(self, repository: GraphRepository):
        self.repository = repository
        
    def extract_service_map(self, service_name: str) -> List[str]:
        """e.g., Frontend -> API -> Auth -> DB"""
        return [