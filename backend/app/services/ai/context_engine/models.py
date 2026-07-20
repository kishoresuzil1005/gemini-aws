"""Core Pydantic v2 models for the AI Context Engine."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .common.constants import ENGINE_VERSION, SCHEMA_VERSION


# ─────────────────────────────────────────────────────────
#  Execution tracking
# ─────────────────────────────────────────────────────────

class ExecutionMetadata(BaseModel):
    """Tracks execution details for a single ContextEngine run.

    Populated incrementally by :class:`~provider_manager.ProviderManager` and
    finalised by :class:`~pipeline.ContextPipeline`.
    """

    providers_executed: List[str] = Field(
        default_factory=list,
        description="Names of providers that completed successfully.",
    )
    providers_failed: List[str] = Field(
        default_factory=list,
        description="Names of providers that raised an exception.",
    )
    cache_hits: int = 0
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    def mark_complete(self) -> None:
        """Set ``end_time`` to now and compute ``duration_seconds``."""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()


# ─────────────────────────────────────────────────────────
#  Canonical context object
# ─────────────────────────────────────────────────────────

class AIContext(BaseModel):
    """Canonical context object returned by the AI Context Engine.

    Design rules
    ------------
    * Treated as **read‑only** once assembled by :class:`~assembler.ContextAssembler`.
    * Each top‑level section corresponds to one provider's ``output_key``.
    * The ``metadata`` block carries engine‑level information (schema version, engine
      version, context level, generation timestamp) so consumers can detect format changes.
    * ``provider_data`` stores the raw standardized response (``metadata`` + ``data``)
      from every provider for debugging and replay.
    """

    # ── Engine-level metadata ──────────────────────────────────────────
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "schema_version": SCHEMA_VERSION,
            "engine_version": ENGINE_VERSION,
            "generated_at": None,   # set by assembler
            "context_level": None,  # set by assembler
        }
    )

    # ── Execution tracking ─────────────────────────────────────────────
    execution: ExecutionMetadata = Field(default_factory=ExecutionMetadata)

    # ── Provider sections ──────────────────────────────────────────────
    resource:       Dict[str, Any] = Field(default_factory=dict)
    graph:          Dict[str, Any] = Field(default_factory=dict)
    inventory:      Dict[str, Any] = Field(default_factory=dict)
    relationships:  Dict[str, Any] = Field(default_factory=dict)
    metrics:        Dict[str, Any] = Field(default_factory=dict)
    cost:           Dict[str, Any] = Field(default_factory=dict)
    security:       Dict[str, Any] = Field(default_factory=dict)
    documentation:  Dict[str, Any] = Field(default_factory=dict)

    # ── Analyzer output sections ───────────────────────────────────────
    findings:        Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)

    # ── Internals ─────────────────────────────────────────────────────
    provider_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw standardized provider responses keyed by provider name.",
    )
    debug: Dict[str, Any] = Field(default_factory=dict)
