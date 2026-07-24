# knowledge/catalog/catalog_query.py
"""API Boundary definitions for querying the Catalog."""

from typing import List, Optional
import abc

from .catalog_models import CanonicalResource

class CatalogQueryAPI(abc.ABC):
    """Abstract interface defining the strict query contract for downstream consumers."""

    @abc.abstractmethod
    def get_resource(self, resource_id: str) -> CanonicalResource:
        pass

    @abc.abstractmethod
    def find_resource(self, alias: str) -> CanonicalResource:
        pass

    @abc.abstractmethod
    def list_resources(self) -> List[CanonicalResource]:
        pass

    @abc.abstractmethod
    def search_by_provider(self, provider: str) -> List[CanonicalResource]:
        pass

    @abc.abstractmethod
    def search_by_service(self, service: str) -> List[CanonicalResource]:
        pass
        
    @abc.abstractmethod
    def search_by_category(self, category: str) -> List[CanonicalResource]:
        pass

    @abc.abstractmethod
    def search_by_tag(self, key: str, value: str) -> List[CanonicalResource]:
        pass
