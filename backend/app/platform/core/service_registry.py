from typing import Dict, Any

class ServiceRegistry:
    """
    Central registry where all platform subsystems (Auth, Billing, Missions) register themselves.
    """
    def __init__(self):
        self._services: Dict[str, Any] = {}

    def register(self, name: str, service_instance: Any):
        print(f"[ServiceRegistry] Registered service: {name}")
        self._services[name] = service_instance

    def get_service(self, name: str) -> Any:
        return self._services.get(name)
        
    def get_all(self) -> Dict[str, Any]:
        return self._services
