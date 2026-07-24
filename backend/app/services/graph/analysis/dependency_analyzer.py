import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from exceptions.analyzer_exceptions import KnowledgeNotFoundError

logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def get_dependencies(self, resource_id: str, depth: int = 5):
        """
        Fetches upstream and downstream dependencies for a given resource
        up to the specified depth.
        """
        # Using Knowledge Service to verify resource existence
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream = self.get_downstream(resource_id, depth)
        upstream = self.get_upstream(resource_id, depth)
        
        return {
            "resource": resource_id,
            "upstream": upstream,
            "downstream": downstream,
            "depth": depth
        }

    def get_downstream(self, resource_id: str, depth: int = 5):
        """Resources that depend ON the given resource (or are connected downstream)."""
        try:
            relationships = self.client.get_relationships(resource_id)
            # Filter for downstream based on relationship type/direction if needed
            # For now, returning all relationships as a simplified downstream response
            return relationships
        except Exception as e:
            logger.error(f"Error querying downstream dependencies: {e}")
            return []

    def get_upstream(self, resource_id: str, depth: int = 5):
        """Resources that the given resource depends ON."""
        try:
            relationships = self.client.get_relationships(resource_id)
            # Filter for upstream based on relationship type/direction if needed
            # For now, returning all relationships as a simplified upstream response
            return relationships
        except Exception as e:
            logger.error(f"Error querying upstream dependencies: {e}")
            return []