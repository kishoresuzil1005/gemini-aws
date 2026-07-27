"""Explainability Engine — Phase 4"""
from __future__ import annotations
from typing import Any, Dict, List
from app.services.ai.orchestrator.models import UnifiedContext


class ExplainabilityEngine:
    """Generates an explanation of how the AI reached its answer."""

    def explain(self, ctx: UnifiedContext) -> Dict[str, Any]:
        providers_used = ctx.quality.providers_executed
        providers_failed = ctx.quality.providers_failed
        evidence_sources = [r.provider for r in ctx.provider_results]
        return {
            "intent": ctx.reasoning.intent.value if ctx.reasoning else "unknown",
            "resource_resolved": ctx.resource.id if ctx.resource else None,
            "confidence": ctx.quality.score,
            "providers_used": providers_used,
            "providers_failed": providers_failed,
            "evidence_sources": evidence_sources,
            "reasoning_explanation": ctx.reasoning.explanation if ctx.reasoning else "",
            "errors": ctx.errors,
        }
