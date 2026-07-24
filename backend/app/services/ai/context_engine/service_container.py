"""Service Container and dependencies for the Context Engine.

This module provides the central Dependency Injection container.
All providers now rely entirely on the Enterprise Knowledge Service
instead of direct provider logic (boto3, postgres, neo4j, etc).
"""

import logging
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Service Container
# -----------------------------------------------------------------------------

class ServiceContainer:
    """
    Central dependency container for the Context Engine.
    Creates and holds one instance of every shared service.
    """
    
    _instance = None

    def __init__(self):
        # Core services
        self.knowledge_client = get_default_client()

    @classmethod
    def instance(cls) -> "ServiceContainer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
