from typing import Dict, Any, Callable
from .service_registry import ServiceRegistry

class LifecycleManager:
    """
    Manages the startup and graceful shutdown sequences of the entire platform.
    """
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.startup_hooks: list[Callable] = []
        self.shutdown_hooks: list[Callable] = []

    def on_startup(self, hook: Callable):
        self.startup_hooks.append(hook)

    def on_shutdown(self, hook: Callable):
        self.shutdown_hooks.append(hook)

    def trigger_startup(self):
        print("[LifecycleManager] Executing startup hooks...")
        for hook in self.startup_hooks:
            hook()
            
    def trigger_shutdown(self):
        print("[LifecycleManager] Executing shutdown hooks...")
        for hook in self.shutdown_hooks:
            hook()
