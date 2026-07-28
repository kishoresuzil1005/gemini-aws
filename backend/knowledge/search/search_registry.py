# knowledge/search/search_registry.py
"""Registry for pluggable index back‑ends.

The current implementation uses a local SQLite FTS5 index (see ``search_index.py``),
but the registry pattern makes it trivial to swap in an Elasticsearch client or
any other searchable store in the future.
"""

from typing import Dict, Callable

class SearchRegistry:
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, factory: Callable):
        """Register a callable that returns an index instance.

        ``factory`` should be a zero‑argument function returning an object that
        implements the ``search`` method used by ``SearchManager``.
        """
        cls._registry[name] = factory

    @classmethod
    def get(cls, name: str):
        if name not in cls._registry:
            raise KeyError(f"Search backend '{name}' not registered")
        return cls._registry[name]()

# Register the default SQLite backend under the name 'sqlite'
from .search_index import get_index as _sqlite_factory
SearchRegistry.register('sqlite', _sqlite_factory)
