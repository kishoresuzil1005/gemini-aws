"""
Confidence Engine — Phase 1 / Phase 5
=======================================
Scores each resolved resource candidate and decides:
  > 0.95  → auto-select
  0.75–0.95 → ask clarification
  < 0.75  → present ranked list
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from app.services.ai.orchestrator.models import ResolvedResource

logger = logging.getLogger(__name__)


class ResolutionDecision(str, Enum):
    AUTO_SELECT = "auto_select"
    ASK_CLARIFICATION = "ask_clarification"
    PRESENT_LIST = "present_list"
    NO_MATCH = "no_match"


@dataclass
class ConfidenceResult:
    decision: ResolutionDecision
    best_match: Optional[ResolvedResource]
    candidates: List[ResolvedResource]
    explanation: str


class ConfidenceEngine:
    """
    Applies source-reliability weights and recency bonuses,
    then makes a final selection decision.
    """

    SOURCE_WEIGHTS = {
        "redis_cache":        1.00,
        "conversation_memory": 0.95,
        "postgres":           0.90,
        "neo4j":              0.85,
        "aws_api":            0.95,
        "tag_store":          0.80,
        "neo4j_fulltext":     0.70,
        "semantic_search":    0.65,
        "llm_fallback":       0.40,
        "regex":              0.95,
        "db_lookup":          0.80,
        "db_lookup_ambiguous":0.50,
        "none":               0.00,
    }

    AUTO_THRESHOLD = 0.93
    CLARIFY_THRESHOLD = 0.72

    def score(self, candidates: List[ResolvedResource]) -> ConfidenceResult:
        """Apply source weights and return the confidence decision."""
        if not candidates:
            return ConfidenceResult(
                decision=ResolutionDecision.NO_MATCH,
                best_match=None,
                candidates=[],
                explanation="No resource candidates found.",
            )

        # Adjust confidence by source weight
        scored = []
        for c in candidates:
            weight = self.SOURCE_WEIGHTS.get(c.source, 0.60)
            adjusted = min(c.confidence * weight + (1 - weight) * c.confidence * 0.5, 1.0)
            scored.append(ResolvedResource(
                resource=c.resource,
                confidence=round(adjusted, 4),
                source=c.source,
            ))

        scored.sort(key=lambda r: r.confidence, reverse=True)
        best = scored[0]

        if best.confidence >= self.AUTO_THRESHOLD:
            decision = ResolutionDecision.AUTO_SELECT
            explanation = (
                f"Auto-selected '{best.resource.id}' "
                f"(confidence={best.confidence:.0%}, source={best.source})"
            )
        elif best.confidence >= self.CLARIFY_THRESHOLD:
            decision = ResolutionDecision.ASK_CLARIFICATION
            explanation = (
                f"Confidence {best.confidence:.0%} — requesting clarification between "
                f"{len(scored)} candidates."
            )
        else:
            decision = ResolutionDecision.PRESENT_LIST
            explanation = (
                f"Low confidence {best.confidence:.0%} — presenting ranked list of "
                f"{len(scored)} candidates."
            )

        logger.info("[ConfidenceEngine] decision=%s best=%s confidence=%.2f",
                    decision, best.resource.id, best.confidence)
        return ConfidenceResult(
            decision=decision,
            best_match=best,
            candidates=scored,
            explanation=explanation,
        )
