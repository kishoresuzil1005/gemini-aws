"""
Scheduler Policy — Production Implementation
Configures and enforces rate limits, priority, and concurrency for discovery runs.
"""
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProviderPolicy:
    """Policy configuration for a specific cloud provider."""
    provider: str
    min_interval_seconds: int = 60        # Minimum time between discovery runs
    max_concurrent_regions: int = 5       # Maximum parallel region scans
    priority: int = 1                     # Higher = runs first (1=low, 10=critical)
    enabled: bool = True
    rate_limit_calls_per_second: float = 10.0  # SDK call rate limit
    retry_on_throttle: bool = True
    backoff_multiplier: float = 2.0       # Exponential backoff factor


class SchedulerPolicy:
    """
    Enforces rate limits, priority ordering, and concurrency caps for discovery jobs.
    """

    DEFAULT_POLICIES: Dict[str, ProviderPolicy] = {
        "aws": ProviderPolicy(
            provider="aws",
            min_interval_seconds=300,       # 5 minutes
            max_concurrent_regions=10,
            priority=5,
            rate_limit_calls_per_second=20.0,
        ),
        "azure": ProviderPolicy(
            provider="azure",
            min_interval_seconds=600,       # 10 minutes
            max_concurrent_regions=5,
            priority=4,
            rate_limit_calls_per_second=10.0,
        ),
        "gcp": ProviderPolicy(
            provider="gcp",
            min_interval_seconds=600,
            max_concurrent_regions=5,
            priority=4,
            rate_limit_calls_per_second=10.0,
        ),
        "kubernetes": ProviderPolicy(
            provider="kubernetes",
            min_interval_seconds=120,       # 2 minutes (k8s is fast)
            max_concurrent_regions=20,      # k8s has many namespaces
            priority=6,
            rate_limit_calls_per_second=50.0,
        ),
    }

    def __init__(self, custom_policies: Optional[Dict[str, ProviderPolicy]] = None):
        self.policies: Dict[str, ProviderPolicy] = {**self.DEFAULT_POLICIES, **(custom_policies or {})}
        self._last_run: Dict[str, float] = {}

    def get_policy(self, provider: str) -> ProviderPolicy:
        return self.policies.get(provider.lower(), ProviderPolicy(provider=provider))

    def can_run(self, provider: str) -> bool:
        """Returns True if the provider is allowed to run based on rate limits."""
        policy = self.get_policy(provider)
        if not policy.enabled:
            return False
        last_run = self._last_run.get(provider, 0)
        elapsed = time.time() - last_run
        if elapsed < policy.min_interval_seconds:
            logger.debug(
                f"{provider} throttled: {elapsed:.0f}s elapsed, need {policy.min_interval_seconds}s"
            )
            return False
        return True

    def record_run(self, provider: str):
        """Records that a discovery run has started for rate-limit enforcement."""
        self._last_run[provider] = time.time()

    def get_priority_order(self, providers: List[str]) -> List[str]:
        """Returns providers ordered by priority (highest first)."""
        return sorted(
            providers,
            key=lambda p: self.get_policy(p).priority,
            reverse=True,
        )

    def get_max_workers(self, provider: str) -> int:
        return self.get_policy(provider).max_concurrent_regions

    def check_rate_limits(self, providers: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Returns a status report of all provider rate limits."""
        target = providers or list(self.policies.keys())
        status = {}
        for provider in target:
            policy = self.get_policy(provider)
            last_run = self._last_run.get(provider, None)
            elapsed = round(time.time() - last_run, 1) if last_run else None
            time_until_allowed = max(0.0, policy.min_interval_seconds - (elapsed or 0))
            status[provider] = {
                "enabled": policy.enabled,
                "priority": policy.priority,
                "can_run_now": self.can_run(provider),
                "min_interval_seconds": policy.min_interval_seconds,
                "elapsed_since_last_run": elapsed,
                "time_until_allowed_seconds": round(time_until_allowed, 1),
                "max_concurrent_regions": policy.max_concurrent_regions,
                "rate_limit_calls_per_second": policy.rate_limit_calls_per_second,
            }
        return status

    def update_policy(self, provider: str, **kwargs) -> ProviderPolicy:
        """Updates a specific policy field for a provider."""
        policy = self.get_policy(provider)
        for k, v in kwargs.items():
            if hasattr(policy, k):
                setattr(policy, k, v)
        self.policies[provider.lower()] = policy
        logger.info(f"Updated policy for {provider}: {kwargs}")
        return policy


# Singleton
scheduler_policy = SchedulerPolicy()