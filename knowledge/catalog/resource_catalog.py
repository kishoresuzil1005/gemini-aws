# knowledge/catalog/resource_catalog.py
"""Unified facade exposing the complete Catalog functionality."""

from typing import List

from .catalog_models import CanonicalResource
from .catalog_index import CatalogIndex
from .catalog_search import CatalogSearch
from .catalog_query import CatalogQueryAPI
from .catalog_manager import CatalogManager
from .catalog_version_manager import CatalogVersionManager
from .catalog_loader import CatalogLoader

class ResourceCatalog(CatalogQueryAPI):
    """The central authoritative registry for Canonical Knowledge Models.
    
    Implements the CatalogQueryAPI to serve as the unified API boundary for
    all downstream systems (Analyzers, Graphs, UIs).
    """

    def __init__(self):
        self.index = CatalogIndex()
        self.version_manager = CatalogVersionManager()
        self.manager = CatalogManager(self.index, self.version_manager)
        self.search_engine = CatalogSearch(self.index)
        self.loader = CatalogLoader()

    # Lifecycle Methods
    
    def ingest(self, resources: List[CanonicalResource]) -> None:
        """Ingest new canonical models into the catalog."""
        self.manager.update_catalog(resources)

    def load_from_disk(self, filepath: str) -> None:
        """Load and index a catalog from disk."""
        resources = self.loader.load(filepath)
        if resources:
            self.manager.update_catalog(resources)

    def save_to_disk(self, filepath: str) -> None:
        """Persist the current catalog to disk."""
        self.loader.save(filepath, self.manager.current_resources)

    # Query API Implementation (O(1) Indexed Lookups)

    def get_resource(self, resource_id: str) -> CanonicalResource:
        return self.search_engine.get_by_id(resource_id)

    def find_resource(self, alias: str) -> CanonicalResource:
        return self.search_engine.search_by_alias(alias)

    def list_resources(self) -> List[CanonicalResource]:
        return self.manager.current_resources

    def search_by_provider(self, provider: str) -> List[CanonicalResource]:
        return self.search_engine.search_by_provider(provider)

    def search_by_service(self, service: str) -> List[CanonicalResource]:
        return self.search_engine.search_by_service(service)
        
    def search_by_category(self, category: str) -> List[CanonicalResource]:
        return self.search_engine.search_by_category(category)

    def search_by_tag(self, key: str, value: str) -> List[CanonicalResource]:
        return self.search_engine.search_by_tag(key, value)
