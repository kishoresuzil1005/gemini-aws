from pydantic import BaseModel
from typing import Dict, Any, Callable

class PluginManifest(BaseModel):
    plugin_id: str
    name: str
    version: str
    author: str
    entry_point: str

class PluginManager:
    """
    Dynamically loads and manages third-party plugins (Terraform, GitHub, Datadog).
    """
    def __init__(self):
        self.loaded_plugins: Dict[str, Any] = {}

    def load_plugin(self, manifest: PluginManifest, module_impl: Any):
        print(f"[PluginManager] Loading plugin: {manifest.name} v{manifest.version}")
        self.loaded_plugins[manifest.plugin_id] = module_impl
        if hasattr(module_impl, "initialize"):
            module_impl.initialize()

    def get_plugin(self, plugin_id: str) -> Any:
        return self.loaded_plugins.get(plugin_id)
