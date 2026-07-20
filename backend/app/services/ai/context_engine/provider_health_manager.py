from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .provider_status import ProviderStatus
from .common.constants import DEFAULT_FAILURE_THRESHOLD


@dataclass
class ProviderHealth:
    provider: str
    status: ProviderStatus
    execution_time_ms: float
    cache_hit: bool
    retries: int
    last_error: Optional[str]
    timestamp: datetime
    failure_count: int = 0
    success_count: int = 0
    circuit_open: bool = False
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


class ProviderHealthManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.providers = {}
        return cls._instance

    def __init__(self):
        pass

    def should_execute(self, provider_name: str) -> bool:
        health = self.providers.get(provider_name)
        if health is None:
            return True
        return not health.circuit_open

    def update(
        self,
        provider: str,
        status: ProviderStatus,
        execution_time_ms: float,
        cache_hit: bool = False,
        retries: int = 0,
        last_error: Optional[str] = None,
    ):
        now = datetime.now(timezone.utc)
        health = self.providers.get(provider)
        
        if health is None:
            health = ProviderHealth(
                provider=provider,
                status=status,
                execution_time_ms=execution_time_ms,
                cache_hit=cache_hit,
                retries=retries,
                last_error=last_error,
                timestamp=now,
            )
            self.providers[provider] = health

        health.status = status
        health.execution_time_ms = execution_time_ms
        health.cache_hit = cache_hit
        health.retries = retries
        health.last_error = last_error
        health.timestamp = now

        if status == ProviderStatus.SUCCESS:
            health.success_count += 1
            health.failure_count = 0
            health.circuit_open = False
            health.last_success = now
        elif status == ProviderStatus.FAILED or status == ProviderStatus.TIMEOUT:
            health.failure_count += 1
            health.last_failure = now
            if health.failure_count >= DEFAULT_FAILURE_THRESHOLD:
                health.circuit_open = True

    def get(self, provider: str):
        return self.providers.get(provider)

    def get_all(self):
        return self.providers

    def summary(self):
        return {
            provider: {
                "status": health.status.value,
                "success_count": health.success_count,
                "failure_count": health.failure_count,
                "execution_time_ms": health.execution_time_ms,
                "cache_hit": health.cache_hit,
                "circuit_open": health.circuit_open,
                "last_success": health.last_success.isoformat() if health.last_success else None,
                "last_failure": health.last_failure.isoformat() if health.last_failure else None,
            }
            for provider, health in self.providers.items()
        }
