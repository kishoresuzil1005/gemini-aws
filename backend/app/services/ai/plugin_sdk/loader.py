"""Dynamic Plugin Loader — Phase 8"""
from __future__ import annotations
import importlib, logging, os, sys
from pathlib import Path
from typing import List, Optional, Type
from .base_plugin import BasePlugin

logger = logging.getLogger(__name__)

_PLUGINS_DIR = Path(__file__).parent / "plugins"


class PluginLoader:
    """
    Discovers and loads plugin classes from the plugins/ directory or
    any registered external path without modifying the orchestrator.
    """

    _loaded: dict = {}

    @classmethod
    def load_from_directory(cls, directory: Optional[Path] = None) -> List[Type[BasePlugin]]:
        directory = directory or _PLUGINS_DIR
        discovered = []
        for fpath in Path(directory).glob("*.py"):
            if fpath.stem.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(fpath.stem, fpath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                        cls._loaded[obj.name] = obj
                        discovered.append(obj)
                        logger.info("[PluginLoader] Loaded plugin: %s v%s", obj.name, obj.version)
            except Exception as e:
                logger.error("[PluginLoader] Failed to load %s: %s", fpath.name, e)
        return discovered

    @classmethod
    def get(cls, name: str) -> Optional[Type[BasePlugin]]:
        return cls._loaded.get(name)

    @classmethod
    def list_plugins(cls) -> List[dict]:
        return [cls().metadata() for cls in cls._loaded.values()]
