# knowledge/service/knowledge_router.py
"""Dispatches generalized service requests to the appropriate subsystem."""

import time
import logging
from typing import Any, List

from .knowledge_response import ResponseBuilder
from .knowledge_models import KnowledgeResponse, Pagination
from .knowledge_query import KnowledgeQuery
from .knowledge_search import KnowledgeSearch
from .knowledge_exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)

class KnowledgeRouter:
    """Invokes the internal catalogs and formats the responses."""
    
    def __init__(self, resource_cat, rel_cat, rule_cat, graph, search_engine: KnowledgeSearch):
        self.resources = resource_cat
        self.relationships = rel_cat
        self.rules = rule_cat
        self.graph = graph
        self.search_engine = search_engine

    def _paginate(self, data: List[Any], query: KnowledgeQuery) -> tuple:
        total = len(data)
        sliced = data[query.offset : query.offset + query.limit]
        has_next = (query.offset + query.limit) < total
        
        pag = Pagination(limit=query.limit, offset=query.offset, total=total, has_next=has_next)
        return sliced, pag

    def handle_get_resource(self, resource_id: str) -> KnowledgeResponse:
        start_time = time.time()
        res = self.resources.get_resource(resource_id) # Raises exception if not found
        return ResponseBuilder.build(data=res, start_time=start_time)

    def handle_list_resources(self, query: KnowledgeQuery) -> KnowledgeResponse:
        start_time = time.time()
        # In a real impl, filters would be applied here
        all_res = self.resources.list_resources()
        sliced, pag = self._paginate(all_res, query)
        return ResponseBuilder.build(data=sliced, start_time=start_time, pagination=pag)

    def handle_find_blast_radius(self, resource_id: str) -> KnowledgeResponse:
        start_time = time.time()
        impact = self.graph.calculate_blast_radius(resource_id)
        return ResponseBuilder.build(data=impact, start_time=start_time)

    def handle_search(self, search_term: str, query: KnowledgeQuery) -> KnowledgeResponse:
        start_time = time.time()
        all_matches = self.search_engine.search_all(search_term)
        sliced, pag = self._paginate(all_matches, query)
        return ResponseBuilder.build(data=sliced, start_time=start_time, pagination=pag)
