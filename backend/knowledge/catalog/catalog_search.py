# knowledge/catalog/catalog_search.py
"""Search capabilities leveraging the in-memory index."""

from typing import List

from .catalog_index import CatalogIndex
from .catalog_models import CanonicalResource
from .catalog_exceptions import ResourceNotFoundError

class CatalogSearch:
    """Executes search and filter operations."""

    def __init__(self, index: CatalogIndex):
        self.index = index

    def _resolve_ids(self, ids: set) -> List[CanonicalResource]:
        return [self.index.id_index[rid] for rid in ids if rid in self.index.id_index]

    def get_by_id(self, resource_id: str) -> CanonicalResource:
        res = self.index.id_index.get(resource_id)
        if not res:
            raise ResourceNotFoundError(f"Resource {resource_id} not found in Catalog.")
        return res

    def search_by_provider(self, provider: str) -> List[CanonicalResource]:
        ids = self.index.provider_index.get(provider.lower(), set())
        return self._resolve_ids(ids)

    def search_by_service(self, service: str) -> List[CanonicalResource]:
        ids = self.index.service_index.get(service.lower(), set())
        return self._resolve_ids(ids)

    def search_by_category(self, category: str) -> List[CanonicalResource]:
        ids = self.index.category_index.get(category.lower(), set())
        return self._resolve_ids(ids)

    def search_by_tag(self, key: str, value: str) -> List[CanonicalResource]:
        tag_key = f"{key}:{value}".lower()
        ids = self.index.tag_index.get(tag_key, set())
        return self._resolve_ids(ids)

    def search_by_alias(self, alias: str) -> CanonicalResource:
        rid = self.index.alias_index.get(alias.lower())
        if not rid:
            raise ResourceNotFoundError(f"No resource found with alias: {alias}")
        return self.get_by_id(rid)
