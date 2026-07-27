"""
Context Aggregator (Phase 9)
=============================
Merges all ProviderResult objects into a single UnifiedContext.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from .models import (
    ContextQualityScore,
    ProviderOutcome,
    ProviderPriority,
    ProviderResult,
    Resource,
    ReasoningResult,
    UnifiedContext,
)

logger = logging.getLogger(__name__)

# Weight table for quality scoring (sum = 1.0)
_PRIORITY_WEIGHT: dict = {
    ProviderPriority.CRITICAL: 0.40,
    ProviderPriority.HIGH: 0.30,
    ProviderPriority.MEDIUM: 0.20,
    ProviderPriority.LOW: 0.10,
}


class ContextAggregator:
    """Merges provider results into a UnifiedContext."""

    def merge(
        self,
        results: List[ProviderResult],
        resource: Optional[Resource] = None,
        reasoning: Optional[ReasoningResult] = None,
        raw_question: str = "",
        session_id: Optional[str] = None,
    ) -> UnifiedContext:
        """Combine all provider outputs into a single context object."""

        executed = [r.provider for r in results if r.outcome == ProviderOutcome.SUCCESS]
        skipped = [r.provider for r in results if r.outcome == ProviderOutcome.SKIPPED]
        failed = [r.provider for r in results if r.outcome in (ProviderOutcome.ERROR, ProviderOutcome.TIMEOUT)]
        errors = [f"[{r.provider}] {r.error}" for r in results if r.error]

        quality_score = self._compute_quality(results)

        ctx = UnifiedContext(
            raw_question=raw_question,
            resource=resource,
            provider_results=results,
            reasoning=reasoning,
            quality=ContextQualityScore(
                score=quality_score,
                providers_executed=executed,
                providers_skipped=skipped,
                providers_failed=failed,
                target_reached=quality_score >= 0.75,
            ),
            errors=errors,
        )

        if session_id:
            ctx.session_id = session_id

        logger.info(
            "[Aggregator] Merged %d providers | quality=%.2f | errors=%d",
            len(results),
            quality_score,
            len(errors),
        )
        return ctx

    # ------------------------------------------------------------------
    def _compute_quality(self, results: List[ProviderResult]) -> float:
        """
        Weighted average of (confidence * completeness * freshness)
        across successful providers, weighted by priority.
        """
        if not results:
            return 0.0

        total_weight = 0.0
        weighted_score = 0.0

        for r in results:
            if r.outcome != ProviderOutcome.SUCCESS:
                continue
            weight = _PRIORITY_WEIGHT.get(r.priority, 0.10)
            score = r.confidence * r.completeness * r.freshness
            weighted_score += weight * score
            total_weight += weight

        if total_weight == 0.0:
            return 0.0

        # Normalise so max weight sums don't inflate the score past 1.0
        return min(weighted_score / total_weight, 1.0)
