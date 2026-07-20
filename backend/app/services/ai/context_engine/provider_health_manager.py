from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .provider_status import ProviderStatus


@dataclass
class ProviderHealth:
    provider: str
    status: ProviderStatus
    execution_time_ms: float
    cache_hit: bool
    retries: int
    last_error: Optional[str]
    timestamp: datetime


class ProviderHealthManager:
    def __init__(self):
        self.providers = {}

    def update(
        self,
        provider,
        status,
        execution_time_ms,
        cache_hit=False,
        retries=0,
        last_error=None,
    ):
        self.providers[provider] = ProviderHealth(
            provider=provider,
            status=status,
            execution_time_ms=execution_time_ms,
            cache_hit=cache_hit,
            retries=retries,
            last_error=last_error,
            timestamp=datetime.utcnow(),
        )

    def get(self, provider):
        return self.providers.get(provider)

    def get_all(self):
        return self.providers
