# knowledge/service/client_factory.py
"""Factory for KnowledgeClient to be used by analyzers."""
from typing import Optional
from .knowledge_client import KnowledgeClient
from .knowledge_service import KnowledgeService
from ..catalog.resource_catalog import ResourceCatalog
from ..relationships.relationship_catalog import RelationshipCatalog
from ..rules.rule_catalog import RuleCatalog
from ..graph.knowledge_graph import KnowledgeGraph

_default_client: Optional[KnowledgeClient] = None

def get_default_client() -> KnowledgeClient:
    """Returns the default KnowledgeClient instance."""
    global _default_client
    if _default_client is None:
        resource_catalog = ResourceCatalog()
        relationship_catalog = RelationshipCatalog()
        rule_catalog = RuleCatalog()
        knowledge_graph = KnowledgeGraph()
        service = KnowledgeService(resource_catalog, relationship_catalog, rule_catalog, knowledge_graph)
        _default_client = KnowledgeClient(service_instance=service)
    return _default_client

def set_default_client(client: KnowledgeClient):
    """Sets the default KnowledgeClient instance."""
    global _default_client
    _default_client = client
