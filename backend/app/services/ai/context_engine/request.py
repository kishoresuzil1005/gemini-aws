from typing import Literal, Optional

from pydantic import BaseModel, Field

from .enums import ContextLevel


class ContextRequest(BaseModel):
    """Parameters for a single Context Engine build invocation."""

    identifier: str
    """Resource identifier – can be an ID, ARN, name, tag query, or natural language."""

    level: ContextLevel = ContextLevel.STANDARD
    """Context level (cumulative – DEEP includes all lower levels)."""

    include_metrics: bool = False
    """Explicit shorthand to include metrics even at a non‑DEEP level."""

    include_cost: bool = False
    """Explicit shorthand to include cost even at a non‑DEEP level."""

    metrics_look_back: int = Field(default=24, ge=1, le=720)
    """How many hours back to fetch metrics data. Default 24 h, max 30 days."""

    cost_granularity: Literal["daily", "hourly"] = "daily"
    """Granularity for cost data. Daily is sufficient for Phase 2."""

    # ---------- reserved for future phases ----------
    # force_refresh: bool = False
    # provider_overrides: Optional[Dict[str, bool]] = None
