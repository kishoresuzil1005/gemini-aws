from typing import Dict, Any

class DependencyContainer:
    """
    Inversion of Control (IoC) container for managing platform dependencies.
    """
    def __init__(self):
        self._providers: Dict[str, Any] = {}

    def provide(self, interface_name: str, implementation: Any):
        self._providers[interface_name] = implementation

    def resolve(self, interface_name: str) -> Any:
        if interface_name not in self._providers:
            raise ValueError(f"Dependency {interface_name} not found.")
        return self._providers[interface_name]
