from typing import List, Dict, Any
from .base_provider import BaseProvider
from .resolved_resource import ResolvedResource
from .request import ContextRequest
from .exceptions import ProviderError
from .cache import CacheBackend
from .models import ExecutionMetadata

class ProviderManager:
    """Executes providers, applies caching, and records execution metadata.
    ``strict`` determines failure handling: ``True`` aborts on the first error,
    ``False`` records the failure and continues.
    The manager returns a mapping of provider name to a dict containing the
    provider instance and the raw data payload. This keeps business data free
    of framework metadata.
    """

    def __init__(self, providers: List[BaseProvider], cache: CacheBackend, strict: bool = True):
        self.providers = providers
        self.cache = cache
        self.strict = strict

    async def run(self, resource: ResolvedResource, request: ContextRequest, exec_meta: ExecutionMetadata) -> Dict[str, Any]:
        payloads: Dict[str, Any] = {}
        for provider in self.providers:
            if not provider.enabled or not provider.supports(request.level):
                continue

            cache_key = None
            if provider.cache_ttl:
                cache_key = f"{provider.name}:{resource.resource_id}:{request.level.value}"
                cached = self.cache.get(cache_key)
                if cached is not None:
                    payloads[provider.name] = cached  # cached entry already contains {'provider': ..., 'data': ...}
                    exec_meta.cache_hits += 1
                    continue

            try:
                data = await provider.fetch(resource, request)
                # Store both provider metadata and data separately
                payload_entry = {"provider": provider, "data": data}
                payloads[provider.name] = payload_entry
                if cache_key:
                    self.cache.put(cache_key, payload_entry, ttl=provider.cache_ttl)
                exec_meta.providers_executed.append(provider.name)
            except Exception as exc:
                exec_meta.providers_failed.append(provider.name)
                if self.strict:
                    raise ProviderError(f"Provider {provider.name} failed: {exc}") from exc
                # tolerant mode – continue
        return payloads
