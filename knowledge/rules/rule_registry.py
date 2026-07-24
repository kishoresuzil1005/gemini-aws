# knowledge/rules/rule_registry.py
"""Registry for internal rule catalog extensions."""

class RuleRegistry:
    """Manages references to specialized rule validators or classifiers if needed."""
    
    def __init__(self):
        self.extensions = {}

    def register(self, name: str, component: any):
        self.extensions[name] = component
