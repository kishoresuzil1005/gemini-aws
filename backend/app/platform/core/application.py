from typing import Dict, Any, Type
from .lifecycle_manager import LifecycleManager
from .service_registry import ServiceRegistry
from .dependency_container import DependencyContainer

class ApplicationKernel:
    """
    The Operating System Kernel for the AI Cloud Platform.
    Boots, orchestrates, and shuts down all underlying services.
    """
    def __init__(self):
        self.registry = ServiceRegistry()
        self.container = DependencyContainer()
        self.lifecycle = LifecycleManager(self.registry)
        
    def start(self):
        print("[Kernel] Booting AI Cloud Operating System...")
        self.lifecycle.trigger_startup()
        print("[Kernel] System is online and ready.")

    def stop(self):
        print("[Kernel] Shutting down AI Cloud Operating System...")
        self.lifecycle.trigger_shutdown()
        print("[Kernel] System offline.")
