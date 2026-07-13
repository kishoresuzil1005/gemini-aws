import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class MigrationPlanner:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)

    def analyze(self, resource_id: str):
        """
        Groups all upstream and downstream resources that need to be 
        migrated together to preserve the application functionality.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        # A migration package involves everything that talks to the resource
        # and everything the resource talks to.
        upstream = self.dependency_analyzer.get_upstream(resource_id, depth=10)
        downstream = self.dependency_analyzer.get_downstream(resource_id, depth=10)
        
        # Deduplicate
        seen = set()
        package = []
        for item in upstream + downstream:
            item_id = item.get("id")
            if item_id and item_id not in seen and item_id != resource_id:
                seen.add(item_id)
                package.append(item)
                
        return {
            "migration_target": resource_id,
            "total_dependencies": len(package),
            "migration_package": package
        