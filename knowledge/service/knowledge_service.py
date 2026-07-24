# knowledge/service/knowledge_service.py
"""The Unified Enterprise Knowledge Service."""

import logging
from typing import Dict, Any

from .knowledge_api import KnowledgeAPI
from .knowledge_query import KnowledgeQuery
from .knowledge_models import KnowledgeResponse
from .knowledge_cache import KnowledgeCache
from .knowledge_router import KnowledgeRouter
from .knowledge_search import KnowledgeSearch
from .knowledge_health import KnowledgeHealth
from .knowledge_statistics import KnowledgeStatistics
from .knowledge_exceptions import ServiceError

logger = logging.getLogger(__name__)

class KnowledgeService(KnowledgeAPI):
    """The absolute API boundary for the Knowledge Platform.
    
    Consumers (Analyzers, AI) MUST use this class instead of importing
    the Catalogs or the Graph directly.
    """

    def __init__(self, resource_catalog, relationship_catalog, rule_catalog, knowledge_graph):
        self.cache = KnowledgeCache()
        self.search_engine = KnowledgeSearch(resource_catalog, relationship_catalog, rule_catalog)
        self.router = KnowledgeRouter(
            resource_catalog, relationship_catalog, rule_catalog, knowledge_graph, self.search_engine
        )
        self.health_monitor = KnowledgeHealth(
            resource_catalog, relationship_catalog, rule_catalog, knowledge_graph
        )
        self.stats_monitor = KnowledgeStatistics(
            resource_catalog, relationship_catalog, rule_catalog, knowledge_graph
        )

    # ---------------------------------------------------------
    # Helper: Caching Decorator-like Logic
    # ---------------------------------------------------------
    def _execute_with_cache(self, cache_key: str, router_func, *args, **kwargs) -> KnowledgeResponse:
        """Checks cache before invoking the router."""
        cached = self.cache.get(cache_key)
        if cached:
            cached.cache_hit = True
            return cached
            
        try:
            response = router_func(*args, **kwargs)
            self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logger.error(f"Service Error on {cache_key}: {e}")
            raise ServiceError(f"Failed to execute query: {str(e)}")

    # ---------------------------------------------------------
    # API Implementation
    # ---------------------------------------------------------

    def get_resource(self, resource_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"res:{resource_id}", 
            self.router.handle_get_resource, 
            resource_id
        )

    def find_resource(self, name: str) -> KnowledgeResponse:
        raise NotImplementedError("find_resource implemented dynamically via router")

    def list_resources(self, query: KnowledgeQuery) -> KnowledgeResponse:
        cache_key = f"list_res:{query.limit}:{query.offset}"
        return self._execute_with_cache(cache_key, self.router.handle_list_resources, query)

    def get_relationship(self, relationship_id: str) -> KnowledgeResponse:
        raise NotImplementedError()

    def find_relationships(self, resource_id: str) -> KnowledgeResponse:
        raise NotImplementedError()

    def find_dependencies(self, resource_id: str) -> KnowledgeResponse:
        raise NotImplementedError()

    def get_rule(self, rule_id: str) -> KnowledgeResponse:
        raise NotImplementedError()

    def list_rules(self, query: KnowledgeQuery) -> KnowledgeResponse:
        raise NotImplementedError()

    def get_node(self, node_id: str) -> KnowledgeResponse:
        raise NotImplementedError()

    def find_shortest_path(self, source_id: str, target_id: str) -> KnowledgeResponse:
        raise NotImplementedError()

    def find_blast_radius(self, resource_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"blast:{resource_id}", 
            self.router.handle_find_blast_radius, 
            resource_id
        )

    def search(self, search_term: str, query: KnowledgeQuery) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"search:{search_term}:{query.limit}:{query.offset}", 
            self.router.handle_search, 
            search_term, 
            query
        )

    def health(self) -> Dict[str, Any]:
        return self.health_monitor.check()

    def statistics(self) -> Dict[str, Any]:
        return self.stats_monitor.get_stats()
