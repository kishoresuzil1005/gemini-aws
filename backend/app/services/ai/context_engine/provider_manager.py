import time
from typing import List, Dict, Any
from .base_provider import BaseProvider
from .resolved_resource import ResolvedResource
from .request import ContextRequest
from .exceptions import ProviderError
from .cache import CacheBackend
from .models import ExecutionMetadata
from .health.provider_health_manager import ProviderHealthManager

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
        
        self.health_manager = ProviderHealthManager()
        for provider in self.providers:
            self.health_manager.register_provider(
                provider.name, 
                source=getattr(provider, "source", None), 
                version=getattr(provider, "version", None)
            )

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
                    self.health_manager.mark_healthy(provider.name, execution_time_ms=0.0, cache_hit=True)
                    continue

            t0 = time.monotonic()
            try:
                data = await provider.fetch(resource, request)
                exec_ms = (time.monotonic() - t0) * 1000
                
                # Store both provider metadata and data separately
                payload_entry = {"provider": provider, "data": data}
                payloads[provider.name] = payload_entry
                if cache_key:
                    self.cache.put(cache_key, payload_entry, ttl=provider.cache_ttl)
                exec_meta.providers_executed.append(provider.name)
                
                if exec_ms > 2000:
                    self.health_manager.mark_degraded(provider.name, execution_time_ms=exec_ms, warning_message="Provider execution was slow")
                else:
                    self.health_manager.mark_healthy(provider.name, execution_time_ms=exec_ms, cache_hit=False)
                    
            except Exception as exc:
                exec_ms = (time.monotonic() - t0) * 1000
                exec_meta.providers_failed.append(provider.name)
                self.health_manager.mark_unavailable(provider.name, error_message=str(exc), execution_time_ms=exec_ms)
                if self.strict:
                    raise ProviderError(f"Provider {provider.name} failed: {exc}") from exc
                # tolerant mode – continue

        # Attach health to context via payloads so we don't need to change AIContext yet
        class HealthDummyProvider:
            output_key = "debug"

        payloads["_health"] = {
            "provider": HealthDummyProvider(),
            "data": {
                "data": {
                    "provider_health": [
                        h.model_dump() for h in self.health_manager.get_all_providers_health()
                    ]
                }
            }
        }
        return payloads
