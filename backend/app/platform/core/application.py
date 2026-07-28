from app.core.logging import get_logger
logger = get_logger(__name__)
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
        logger.debug("[Kernel] Booting AI Cloud Operating System...")
        self.lifecycle.trigger_startup()
        logger.debug("[Kernel] System is online and ready.")

    def stop(self):
        logger.debug("[Kernel] Shutting down AI Cloud Operating System...")
        self.lifecycle.trigger_shutdown()
        logger.debug("[Kernel] System offline.")
