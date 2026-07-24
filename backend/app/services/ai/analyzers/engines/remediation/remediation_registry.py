"""
Remediation Registry for discovering and managing Generator Plugins.
"""
import importlib
import pkgutil
import inspect
import logging
from typing import Dict, List, Type
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator

logger = logging.getLogger(__name__)

class RemediationRegistry:
    """
    Auto-discovers and indexes RemediationGenerator implementations.
    """
    
    def __init__(self):
        self._generators: Dict[str, RemediationGenerator] = {}
        self.discover()
        
    def discover(self):
        """Walk the remediation/generators package and instantiate plugins."""
        try:
            import app.services.ai.analyzers.engines.remediation.generators as generators_pkg
            package_name = generators_pkg.__name__
            package_path = generators_pkg.__path__
            
            for _, module_name, _ in pkgutil.walk_packages(package_path, package_name + "."):
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, RemediationGenerator) and obj is not RemediationGenerator:
                        instance = obj()
                        self.register(instance)
        except Exception as e:
            logger.error(f"Error discovering remediation generators: {e}")

    def register(self, generator: RemediationGenerator):
        fmt = generator.get_format()
        if fmt in self._generators:
            logger.warning(f"Generator for format {fmt} already registered. Overwriting.")
        self._generators[fmt] = generator
        
    def unregister(self, fmt: str):
        if fmt in self._generators:
            del self._generators[fmt]
            
    def replace(self, generator: RemediationGenerator):
        self.register(generator)
        
    def find_generator(self, fmt: str) -> RemediationGenerator:
        return self._generators.get(fmt)
        
    def list_generators(self) -> List[str]:
        return list(self._generators.keys())
