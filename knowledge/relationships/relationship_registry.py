# knowledge/relationships/relationship_registry.py
"""Registry for internal relationship catalog extensions."""

class RelationshipRegistry:
    """Manages references to specialized relationship parsers or validators."""
    
    def __init__(self):
        self.extensions = {}

    def register(self, name: str, component: any):
        self.extensions[name] = component
