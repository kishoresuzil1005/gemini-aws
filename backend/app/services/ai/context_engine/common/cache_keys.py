"""Cache key builders for provider results.

Keys follow the pattern:
    <provider_name>:<resource_id>:<context_level>
"""

from ..enums import ContextLevel


def provider_cache_key(provider_name: str, resource_id: str, level: ContextLevel) -> str:
    """Build a deterministic cache key for a provider result."""
    return f"{provider_name}:{resource_id}:{level.value}"


def resource_cache_key(resource_id: str) -> str:
    """Build a cache key for a resolved resource."""
    return f"resolved_resource:{resource_id}"
