"""
Provider Registry
=================
Dynamic registration and lookup of context providers.
Every provider self-registers on import; the orchestrator queries
the registry to know which providers are available for a given intent.
"""

from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, Type

from .models import ProviderPriority

logger = logging.getLogger(__name__)


class ProviderRegistration:
    """Metadata about a registered provider."""

    def __init__(
        self,
        name: str,
        factory: Callable,
        priority: ProviderPriority = ProviderPriority.MEDIUM,
        intents: Optional[List[str]] = None,
    ):
        self.name = name
        self.factory = factory
        self.priority = priority
        self.intents = intents or []   # empty = matches all intents


class ProviderRegistry:
    """Singleton registry for context providers."""

    _instance: Optional["ProviderRegistry"] = None
    _providers: Dict[str, ProviderRegistration] = {}

    @classmethod
    def get_instance(cls) -> "ProviderRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(
        self,
        name: str,
        factory: Callable,
        priority: ProviderPriority = ProviderPriority.MEDIUM,
        intents: Optional[List[str]] = None,
    ) -> None:
        """Register a provider factory under *name*."""
        self._providers[name] = ProviderRegistration(
            name=name, factory=factory, priority=priority, intents=intents or []
        )
        logger.info("[ProviderRegistry] Registered provider: %s (priority=%s)", name, priority)

    def get(self, name: str) -> Optional[ProviderRegistration]:
        return self._providers.get(name)

    def list_for_intent(self, intent: str) -> List[ProviderRegistration]:
        """Return providers that match *intent*, sorted by priority (critical first)."""
        priority_order = {
            ProviderPriority.CRITICAL: 0,
            ProviderPriority.HIGH: 1,
            ProviderPriority.MEDIUM: 2,
            ProviderPriority.LOW: 3,
        }
        matching = [
            reg for reg in self._providers.values()
            if not reg.intents or intent in reg.intents
        ]
        return sorted(matching, key=lambda r: priority_order.get(r.priority, 99))

    def all(self) -> List[ProviderRegistration]:
        return list(self._providers.values())

    def clear(self) -> None:
        """Clear all registrations (useful for tests)."""
        self._providers.clear()
