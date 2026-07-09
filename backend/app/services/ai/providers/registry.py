from typing import Dict, Any, List

class ContextProviderRegistry:
    """
    Registry for reusable AI Context Providers (Graph, Inventory, Cost, Documentation).
    Allows the AIEngine to dynamically pull context from different subsystems.
    """
    
    def __init__(self):
        self._providers = {}
        
    def register(self, name: str, provider: Any):
        self._providers[name] = provider
        
    def get_provider(self, name: str) -> Any:
        return self._providers.get(name)
        
    def build_context(self, scopes: List[str], resource_id: str = None) -> Dict[str, Any]:
        context = {}
        for scope in scopes:
            provider = self.get_provider(scope)
            if provider:
                context[scope] = provider.get_context(resource_id)
        return context
