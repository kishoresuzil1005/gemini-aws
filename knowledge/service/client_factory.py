# knowledge/service/client_factory.py
"""Factory for KnowledgeClient to be used by analyzers."""
from typing import Optional
from .knowledge_client import KnowledgeClient

_default_client: Optional[KnowledgeClient] = None

def get_default_client() -> KnowledgeClient:
    """Returns the default KnowledgeClient instance."""
    global _default_client
    if _default_client is None:
        # For now, we instantiate it with a None service or mock
        # In a real app, this should be initialized at startup with the real KnowledgeService
        _default_client = KnowledgeClient(service_instance=None)
    return _default_client

def set_default_client(client: KnowledgeClient):
    """Sets the default KnowledgeClient instance."""
    global _default_client
    _default_client = client
