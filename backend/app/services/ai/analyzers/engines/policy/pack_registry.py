"""
Pack Registry for Policy Engine.
"""
import importlib
import pkgutil
import inspect
import logging
from typing import Dict, List, Optional
from app.services.ai.analyzers.engines.policy.policy_models import PolicyPack

logger = logging.getLogger(__name__)

class PackRegistry:
    """
    Discovers and manages Policy Packs via pkgutil.
    """
    def __init__(self):
        self._packs: Dict[str, PolicyPack] = {}
        self.discover()
        
    def discover(self):
        try:
            import app.services.ai.analyzers.engines.policy.packs as packs_pkg
            package_name = packs_pkg.__name__
            package_path = packs_pkg.__path__
            
            for _, module_name, _ in pkgutil.walk_packages(package_path, package_name + "."):
                module = importlib.import_module(module_name)
                
                # Assume each pack module exposes a PACK variable of type PolicyPack
                if hasattr(module, "PACK"):
                    pack = getattr(module, "PACK")
                    if isinstance(pack, PolicyPack):
                        self.register(pack)
        except Exception as e:
            logger.error(f"Error discovering policy packs: {e}")

    def register(self, pack: PolicyPack):
        if pack.metadata.id in self._packs:
            logger.warning(f"Pack {pack.metadata.id} already registered. Overwriting.")
        self._packs[pack.metadata.id] = pack
        
    def get_pack(self, pack_id: str) -> Optional[PolicyPack]:
        return self._packs.get(pack_id)
        
    def list_packs(self) -> List[str]:
        return list(self._packs.keys())
