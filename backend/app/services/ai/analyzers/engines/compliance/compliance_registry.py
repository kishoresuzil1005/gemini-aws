"""
Compliance Registry for discovering and managing Framework Definitions.
"""
import importlib
import pkgutil
import inspect
import logging
from typing import Dict, List, Type
from app.services.ai.analyzers.engines.compliance.compliance_framework import ComplianceFrameworkDefinition
from app.services.ai.analyzers.engines.compliance.compliance_models import ComplianceFramework

logger = logging.getLogger(__name__)

class ComplianceRegistry:
    """
    Auto-discovers and indexes ComplianceFrameworkDefinition implementations.
    """
    
    def __init__(self):
        self._frameworks: Dict[ComplianceFramework, ComplianceFrameworkDefinition] = {}
        self.discover()
        
    def discover(self):
        """Walk the compliance/frameworks package and instantiate plugins."""
        try:
            import app.services.ai.analyzers.engines.compliance.frameworks as frameworks_pkg
            package_name = frameworks_pkg.__name__
            package_path = frameworks_pkg.__path__
            
            for _, module_name, _ in pkgutil.walk_packages(package_path, package_name + "."):
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, ComplianceFrameworkDefinition) and obj is not ComplianceFrameworkDefinition:
                        instance = obj()
                        self.register(instance)
        except Exception as e:
            logger.error(f"Error discovering compliance frameworks: {e}")

    def register(self, framework: ComplianceFrameworkDefinition):
        fw_type = framework.get_framework_type()
        if fw_type in self._frameworks:
            logger.warning(f"Framework {fw_type} already registered. Overwriting.")
        self._frameworks[fw_type] = framework
        
    def unregister(self, fw_type: ComplianceFramework):
        if fw_type in self._frameworks:
            del self._frameworks[fw_type]
            
    def replace(self, framework: ComplianceFrameworkDefinition):
        self.register(framework)
        
    def get_framework(self, fw_type: ComplianceFramework) -> ComplianceFrameworkDefinition:
        return self._frameworks.get(fw_type)
        
    def list_frameworks(self) -> List[ComplianceFramework]:
        return list(self._frameworks.keys())
