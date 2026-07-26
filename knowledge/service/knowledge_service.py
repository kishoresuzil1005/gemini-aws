# knowledge/service/knowledge_service.py
"""The Unified Enterprise Knowledge Service."""

import logging
from typing import Dict, Any

from .knowledge_api import KnowledgeAPI
from .lifecycle import Lifecycle
from .knowledge_query import KnowledgeQuery
from .knowledge_models import KnowledgeResponse
from .knowledge_cache import KnowledgeCache
from .knowledge_router import KnowledgeRouter
from .knowledge_search import KnowledgeSearch
from .knowledge_health import KnowledgeHealth
from .knowledge_statistics import KnowledgeStatistics
from .knowledge_exceptions import ServiceError

logger = logging.getLogger(__name__)

class KnowledgeService(KnowledgeAPI, Lifecycle):
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
        self._is_ready = False

    def initialize(self) -> None:
        logger.info("Initializing KnowledgeService...")

    def start(self) -> None:
        logger.info("Starting KnowledgeService...")
        self._is_ready = True

    def ready(self) -> bool:
        return self._is_ready

    def shutdown(self) -> None:
        logger.info("Shutting down KnowledgeService...")
        self._is_ready = False

    def dispose(self) -> None:
        logger.info("Disposing KnowledgeService...")
        self.cache = None

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
        return self._execute_with_cache(
            f"find_res:{name}", 
            self.router.handle_find_resource, 
            name
        )

    def list_resources(self, query: KnowledgeQuery) -> KnowledgeResponse:
        cache_key = f"list_res:{query.limit}:{query.offset}"
        return self._execute_with_cache(cache_key, self.router.handle_list_resources, query)

    def get_relationship(self, relationship_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"rel:{relationship_id}",
            self.router.handle_get_relationship,
            relationship_id
        )

    def find_relationships(self, resource_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"find_rels:{resource_id}",
            self.router.handle_find_relationships,
            resource_id
        )

    def find_dependencies(self, resource_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"deps:{resource_id}",
            self.router.handle_find_dependencies,
            resource_id
        )

    def get_rule(self, rule_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"rule:{rule_id}",
            self.router.handle_get_rule,
            rule_id
        )

    def list_rules(self, query: KnowledgeQuery) -> KnowledgeResponse:
        cache_key = f"list_rules:{query.limit}:{query.offset}"
        return self._execute_with_cache(cache_key, self.router.handle_list_rules, query)

    def get_node(self, node_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"node:{node_id}",
            self.router.handle_get_node,
            node_id
        )

    def find_shortest_path(self, source_id: str, target_id: str) -> KnowledgeResponse:
        return self._execute_with_cache(
            f"path:{source_id}:{target_id}",
            self.router.handle_find_shortest_path,
            source_id,
            target_id
        )

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
