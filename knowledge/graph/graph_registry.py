# knowledge/graph/graph_registry.py
"""Registry for internal graph catalog extensions."""

class GraphRegistry:
    """Manages references to specialized graph analytics or custom traversals."""
    
    def __init__(self):
        self.extensions = {}

    def register(self, name: str, component: any):
        self.extensions[name] = component
