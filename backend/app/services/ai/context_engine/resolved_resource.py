from typing import Any, Dict, Optional
from pydantic import BaseModel


class ResolvedResource(BaseModel):
    """Canonical representation of a resource after identifier resolution.

    ``resource_id`` is the authoritative identifier used by providers
    (i.e. the value stored in the PostgreSQL ``resources`` table).

    ``original_identifier`` is whatever the user typed (e.g. ``cloudops-db``).
    """

    # Core identity ──────────────────────────────────────────────────────────
    resource_id: str
    original_identifier: str

    # Populated by the resolver when a PostgreSQL match is found ─────────────
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    provider: Optional[str] = None
    region: Optional[str] = None
    account_id: Optional[str] = None
    arn: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    # ─── Helpers ────────────────────────────────────────────────────────────
    @property
    def display_name(self) -> str:
        return self.resource_name or self.resource_id

    @property
    def is_fully_resolved(self) -> bool:
        """True when a real DB row was found (type is known)."""
        return bool(self.resource_type)
