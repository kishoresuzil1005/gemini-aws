import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from exceptions.analyzer_exceptions import KnowledgeNotFoundError

logger = logging.getLogger(__name__)

class MigrationPlanner:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.dependency_analyzer = DependencyAnalyzer(self.client)

    def analyze(self, resource_id: str):
        """
        Groups all upstream and downstream resources that need to be 
        migrated together to preserve the application functionality.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        # A migration package involves everything that talks to the resource
        # and everything the resource talks to.
        upstream = self.dependency_analyzer.get_upstream(resource_id, depth=10)
        downstream = self.dependency_analyzer.get_downstream(resource_id, depth=10)
        
        # Deduplicate
        seen = set()
        package = []
        for item in upstream + downstream:
            item_id = item.get("id") or item.get("target") or item.get("source")
            if item_id and item_id not in seen and item_id != resource_id:
                seen.add(item_id)
                package.append(item)
                
        return {
            "migration_target": resource_id,
            "total_dependencies": len(package),
            "migration_package": package
        }