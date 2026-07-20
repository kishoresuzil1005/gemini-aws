from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

from .provider_status import ProviderStatus
from .health_models import ProviderHealth

logger = logging.getLogger(__name__)

class ProviderHealthManager:
    """Manages the health status of all Context Engine providers."""
    
    def __init__(self):
        self._health_store: Dict[str, ProviderHealth] = {}

    def register_provider(self, provider_name: str, source: Optional[str] = None, version: Optional[str] = None) -> None:
        """Register a new provider with an UNKNOWN status."""
        if provider_name not in self._health_store:
            self._health_store[provider_name] = ProviderHealth(
                provider_name=provider_name,
                status=ProviderStatus.UNKNOWN,
                source=source,
                version=version,
            )

    def update_health(self, provider_name: str, **kwargs) -> None:
        """Update any attributes of a provider's health object."""
        if provider_name in self._health_store:
            health = self._health_store[provider_name]
            for key, value in kwargs.items():
                if hasattr(health, key):
                    setattr(health, key, value)
            health.last_checked = datetime.now(timezone.utc)
        else:
            logger.warning("Attempted to update health for unregistered provider: %s", provider_name)

    def mark_healthy(self, provider_name: str, execution_time_ms: float = 0.0, cache_hit: bool = False) -> None:
        """Mark a provider as HEALTHY."""
        self.update_health(
            provider_name,
            status=ProviderStatus.HEALTHY,
            execution_time_ms=execution_time_ms,
            cache_hit=cache_hit,
            error_message=None
        )

    def mark_degraded(self, provider_name: str, execution_time_ms: float, warning_message: Optional[str] = None) -> None:
        """Mark a provider as DEGRADED (e.g., if it took too long)."""
        self.update_health(
            provider_name,
            status=ProviderStatus.DEGRADED,
            execution_time_ms=execution_time_ms,
            warning_message=warning_message
        )

    def mark_unavailable(self, provider_name: str, error_message: str, execution_time_ms: float = 0.0) -> None:
        """Mark a provider as UNAVAILABLE (e.g., if it threw an exception)."""
        self.update_health(
            provider_name,
            status=ProviderStatus.UNAVAILABLE,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )

    def get_provider_health(self, provider_name: str) -> Optional[ProviderHealth]:
        """Get the health model for a single provider."""
        return self._health_store.get(provider_name)

    def get_all_providers_health(self) -> List[ProviderHealth]:
        """Get the health models for all providers."""
        return list(self._health_store.values())

    def reset_health(self, provider_name: str) -> None:
        """Reset a provider's health to UNKNOWN."""
        if provider_name in self._health_store:
            current = self._health_store[provider_name]
            self._health_store[provider_name] = ProviderHealth(
                provider_name=provider_name,
                source=current.source,
                version=current.version
            )
