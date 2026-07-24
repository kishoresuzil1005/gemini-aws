# knowledge/service/knowledge_client.py
"""Knowledge Client Wrapper for Analyzers.

This client provides a thin, provider-independent facade over the Enterprise Knowledge
Service for all analyzers. It translates service responses into a format easily
consumable by analyzers and hides the underlying service complexity.
"""
import logging
from typing import Dict, Any, List, Optional
from .knowledge_models import KnowledgeResponse, KnowledgeQuery

logger = logging.getLogger(__name__)

class KnowledgeClientError(Exception):
    """Base exception for Knowledge Client errors."""
    pass

class KnowledgeNotFoundError(KnowledgeClientError):
    """Raised when requested knowledge cannot be found."""
    pass

class KnowledgeClient:
    def __init__(self, service_instance):
        """
        Initializes the client with an active KnowledgeService instance.
        """
        self.service = service_instance

    def _extract_data(self, response: KnowledgeResponse) -> Any:
        """Extracts data from a successful response or raises an error."""
        if not response.success:
            raise KnowledgeClientError(f"Service returned error: {response.error}")
        return response.data

    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single resource by ID."""
        try:
            res = self.service.get_resource(resource_id)
            return self._extract_data(res)
        except Exception as e:
            if "not found" in str(e).lower():
                return None
            logger.error(f"Error getting resource {resource_id}: {e}")
            raise KnowledgeClientError(f"Failed to get resource: {e}")

    def search_resources(self, query_str: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Searches for resources matching the query."""
        try:
            query = KnowledgeQuery(limit=limit)
            res = self.service.search(query_str, query)
            data = self._extract_data(res)
            return data if isinstance(data, list) else [data] if data else []
        except Exception as e:
            logger.error(f"Error searching resources with query '{query_str}': {e}")
            raise KnowledgeClientError(f"Failed to search resources: {e}")

    def get_relationships(self, resource_id: str) -> List[Dict[str, Any]]:
        """Retrieves relationships for a given resource."""
        # Using search as a fallback since specific methods might not be fully implemented in KS yet
        try:
             # Ideally this maps to self.service.find_relationships(resource_id)
             # but we'll use a generic approach if that's not ready
            query = KnowledgeQuery(limit=100)
            res = self.service.search(f"relationships:{resource_id}", query)
            data = self._extract_data(res)
            return data if isinstance(data, list) else [data] if data else []
        except Exception as e:
            logger.error(f"Error getting relationships for {resource_id}: {e}")
            return []

    def get_rules(self, category: str = None) -> List[Dict[str, Any]]:
        """Retrieves rules, optionally filtered by category."""
        try:
             # Similarly, mapping to search or list_rules
            query = KnowledgeQuery(limit=100)
            search_str = f"category:{category}" if category else "type:rule"
            res = self.service.search(search_str, query)
            data = self._extract_data(res)
            return data if isinstance(data, list) else [data] if data else []
        except Exception as e:
            logger.error(f"Error getting rules for category '{category}': {e}")
            return []
            
    def query_graph(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Allows direct, provider-agnostic queries against the knowledge graph."""
        try:
             # Try to see if service has query method
            if hasattr(self.service, "query"):
                res = self.service.query(query, **kwargs)
                return self._extract_data(res) if hasattr(res, "success") else res
            else:
                raise NotImplementedError("Direct graph querying via KS not yet supported.")
        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"Error executing graph query: {e}")
            raise KnowledgeClientError(f"Failed to query graph: {e}")

    def get_resource_subgraph(self, resource_id: str) -> Dict[str, Any]:
        """Gets a resource subgraph (nodes and edges)."""
        try:
            if hasattr(self.service, "get_resource_subgraph"):
                res = self.service.get_resource_subgraph(resource_id)
                return self._extract_data(res) if hasattr(res, "success") else res
            
            # Fallback
            resource = self.get_resource(resource_id)
            if not resource:
                return {"resource": {}, "subgraph": {"nodes": [], "edges": []}}
            return {
                "resource": resource,
                "subgraph": {
                    "nodes": [resource],
                    "edges": self.get_relationships(resource_id)
                }
            }
        except Exception as e:
            logger.error(f"Error getting subgraph for {resource_id}: {e}")
            return {"resource": {}, "subgraph": {"nodes": [], "edges": []}}
