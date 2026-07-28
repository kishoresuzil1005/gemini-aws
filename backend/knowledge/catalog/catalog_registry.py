# knowledge/catalog/catalog_registry.py
"""Registry for internal catalog plugin components."""

class CatalogRegistry:
    """Manages references to specialized catalog engines if needed."""
    
    def __init__(self):
        self.extensions = {}

    def register(self, name: str, component: any):
        self.extensions[name] = component
