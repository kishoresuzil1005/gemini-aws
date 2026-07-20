"""Assembles raw provider payloads into a canonical :class:`~models.AIContext`.

Design rules
------------
* No provider‑specific logic lives here.
* Relies on each provider exposing an ``output_key`` that maps to a field on
  :class:`~models.AIContext`.
* Every provider now returns ``{"metadata": {...}, "data": {...}}``.
  The assembler stores the full envelope in ``provider_data`` for debugging and
  places only the ``data`` portion into the matching top‑level context section.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from .models import AIContext, ExecutionMetadata
from .enums import ContextLevel


class ContextAssembler:
    """Merge provider payloads into a :class:`~models.AIContext`."""

    def assemble(
        self,
        payloads: Dict[str, Any],
        exec_meta: ExecutionMetadata,
        level: ContextLevel,
    ) -> AIContext:
        """Merge *payloads* into an :class:`~models.AIContext`.

        Parameters
        ----------
        payloads:
            Mapping of provider name → standardized ``{"metadata": ..., "data": ...}``
            response (produced by :class:`~provider_manager.ProviderManager`).
        exec_meta:
            Execution metadata populated by :class:`~provider_manager.ProviderManager`.
        level:
            The :class:`~enums.ContextLevel` used for this request.
        """
        now = datetime.now(timezone.utc).isoformat()

        context_data: Dict[str, Any] = {
            "metadata": {
                "schema_version": None,   # default_factory fills this
                "engine_version": None,   # default_factory fills this
                "generated_at": now,
                "context_level": level.value,
            },
            "execution": exec_meta,
            "resource": {},
            "graph": {},
            "inventory": {},
            "relationships": {},
            "metrics": {},
            "cost": {},
            "security": {},
            "documentation": {},
            "findings": {},
            "recommendations": {},
            "provider_data": {},
            "debug": {},
        }

        for provider_name, response in payloads.items():
            # response shape: {"metadata": {...}, "data": {...}, "provider": <obj>}
            provider_obj  = response.get("provider")
            std_payload   = response.get("data", {})   # this IS the StandardProviderResponse

            # Store the full standardized payload for debugging / replay
            context_data["provider_data"][provider_name] = std_payload

            # Place only the ``data`` block into the matching AIContext section
            output_key = getattr(provider_obj, "output_key", None)
            if output_key and output_key in context_data:
                inner_data = std_payload.get("data", std_payload) if isinstance(std_payload, dict) else std_payload
                context_data[output_key] = inner_data

        ctx = AIContext(**context_data)
        # Merge the schema/engine version from the default_factory
        ctx.metadata["schema_version"] = ctx.metadata.get("schema_version") or AIContext.__fields__["metadata"].default_factory()["schema_version"]  # type: ignore
        ctx.metadata["engine_version"]  = ctx.metadata.get("engine_version")  or AIContext.__fields__["metadata"].default_factory()["engine_version"]   # type: ignore
        return ctx
