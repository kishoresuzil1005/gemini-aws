import time
import asyncio
import logging
from typing import List, Dict, Any
from .base_provider import BaseProvider
from .resolved_resource import ResolvedResource
from .request import ContextRequest
from .exceptions import ProviderError
from .cache import CacheBackend
from .models import ExecutionMetadata
from .provider_health_manager import ProviderHealthManager
from .provider_status import ProviderStatus
from .common.constants import DEFAULT_PROVIDER_TIMEOUT

logger = logging.getLogger(__name__)

class ProviderManager:
    """Executes providers, applies caching, and records execution metadata.
    ``strict`` determines failure handling: ``True`` aborts on the first error,
    ``False`` records the failure and continues.
    The manager returns a mapping of provider name to a dict containing the
    provider instance and the raw data payload. This keeps business data free
    of framework metadata.
    """

    def __init__(self, providers: List[BaseProvider], cache: CacheBackend, strict: bool = True):
        self.providers = sorted(providers, key=lambda p: getattr(p, "priority", 100))
        self.cache = cache
        self.strict = strict
        self.health = ProviderHealthManager()

    async def run(self, resource: ResolvedResource, request: ContextRequest, exec_meta: ExecutionMetadata) -> Dict[str, Any]:
        payloads: Dict[str, Any] = {}
        for provider in self.providers:
            is_supported = provider.supports(request.level)
            
            if provider.name == "metrics" and getattr(request, "include_metrics", False):
                is_supported = True
            if provider.name == "cost" and getattr(request, "include_cost", False):
                is_supported = True
                
            if not provider.enabled or not is_supported:
                continue

            cache_key = None
            if provider.cache_ttl:
                cache_key = f"{provider.name}:{resource.resource_id}:{request.level.value}"
                cached = self.cache.get(cache_key)
                if cached is not None:
                    payloads[provider.name] = cached  # cached entry already contains {'provider': ..., 'data': ...}
                    exec_meta.cache_hits += 1
                    self.health.update(
                        provider=provider.name,
                        status=ProviderStatus.CACHE_HIT,
                        execution_time_ms=0.0,
                        cache_hit=True,
                    )
                    continue

            t0 = time.monotonic()
            try:
                data = await asyncio.wait_for(
                    provider.fetch(resource, request),
                    timeout=getattr(provider, "timeout", DEFAULT_PROVIDER_TIMEOUT)
                )
                exec_ms = (time.monotonic() - t0) * 1000
                
                valid, reason = self._is_valid_response(data)
                if not valid:
                    self.health.update(
                        provider=provider.name,
                        status=ProviderStatus.INVALID_RESPONSE,
                        execution_time_ms=exec_ms,
                        last_error=reason,
                    )
                    continue
                
                payload_entry = {"provider": provider, "data": data}
                payloads[provider.name] = payload_entry
                if cache_key:
                    self.cache.put(cache_key, payload_entry, ttl=provider.cache_ttl)
                exec_meta.providers_executed.append(provider.name)

                self.health.update(
                    provider=provider.name,
                    status=ProviderStatus.SUCCESS,
                    execution_time_ms=exec_ms,
                    cache_hit=False,
                )
                    
            except asyncio.TimeoutError:
                exec_ms = (time.monotonic() - t0) * 1000
                self.health.update(
                    provider=provider.name,
                    status=ProviderStatus.TIMEOUT,
                    execution_time_ms=exec_ms,
                    last_error="Provider execution timed out",
                )
                logger.warning("%s timed out", provider.name)
                continue
                
            except Exception as exc:
                exec_ms = (time.monotonic() - t0) * 1000
                exec_meta.providers_failed.append(provider.name)
                self.health.update(
                    provider=provider.name,
                    status=ProviderStatus.FAILED,
                    execution_time_ms=exec_ms,
                    last_error=str(exc),
                )
                if self.strict:
                    raise ProviderError(f"Provider {provider.name} failed: {exc}") from exc
                # tolerant mode – continue

        from dataclasses import asdict
        
        # Attach health to context via payloads so we don't need to change AIContext yet
        class HealthDummyProvider:
            output_key = "debug"

        payloads["_health"] = {
            "provider": HealthDummyProvider(),
            "data": {
                "data": {
                    "provider_health": [
                        asdict(h) for h in self.health.get_all().values()
                    ]
                }
            }
        }
        return payloads

    def provider_health(self):
        return self.health.get_all()

    def _is_valid_response(self, result) -> tuple[bool, str]:
        if result is None:
            return False, "Provider returned None"
        if not isinstance(result, dict):
            return False, "Provider response is not a dictionary"
        if "metadata" not in result:
            return False, "Missing metadata block"
        if "data" not in result:
            return False, "Missing data block"
            
        metadata = result["metadata"]
        if not isinstance(metadata, dict):
            return False, "Metadata is invalid"
            
        required = ["provider", "status"]
        for key in required:
            if key not in metadata:
                return False, f"Missing metadata field: {key}"
                
        return True, ""
