# knowledge/snapshot/snapshot_registry.py
"""Registry for internal snapshot extensions."""

class SnapshotRegistry:
    """Manages references to specialized storage backends or export plugins."""
    
    def __init__(self):
        self.extensions = {}

    def register(self, name: str, component: any):
        self.extensions[name] = component
