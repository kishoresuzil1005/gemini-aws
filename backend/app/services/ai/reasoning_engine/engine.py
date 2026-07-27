"""
Infrastructure Reasoning Engine — Phase 1 / Phase 3
=====================================================
Pure-logic engine that maps user intent → ReasoningResult.
Never calls an LLM. Never does I/O. Only applies rules.

Pipeline:
  raw_question → EntityExtractor → IntentClassifier → RuleSet → ReasoningResult
"""

from __future__ import annotations

import logging
from typing import List, Optional

from app.services.ai.orchestrator.models import (
    CandidateQuery,
    IntentCategory,
    ReasoningResult,
)
from .entity_extractor import EntityExtractor
from .rule_set import required_providers

logger = logging.getLogger(__name__)

# Keyword → IntentCategory mapping (fast path — no LLM needed)
_INTENT_KEYWORDS: dict = {
    IntentCategory.HEALTH_CHECK: [
        "unhealthy", "health", "status", "failing", "broken", "down", "not working",
        "why is", "what is wrong", "issue", "problem",
    ],
    IntentCategory.SECURITY_AUDIT: [
        "security", "secure", "insecure", "vulnerability", "risk", "exposed",
        "public", "open port", "audit", "compliance", "guardduty", "inspector",
    ],
    IntentCategory.COST_ANALYSIS: [
        "cost", "spend", "bill", "expensive", "savings", "waste", "optimize cost",
        "right size", "rightsizing",
    ],
    IntentCategory.PERFORMANCE: [
        "slow", "latency", "performance", "cpu", "memory", "throughput", "bottleneck",
        "timeout", "overloaded",
    ],
    IntentCategory.RELATIONSHIP_QUERY: [
        "depends", "dependency", "connected", "relationship", "upstream", "downstream",
        "blast radius", "what breaks", "impact",
    ],
    IntentCategory.REMEDIATION: [
        "fix", "repair", "remediate", "restart", "reboot", "resolve", "terraform",
        "cloudformation", "aws cli", "automate", "rollback",
    ],
}


def _classify_intent(question: str) -> tuple[IntentCategory, float]:
    """
    Rule-based intent classification.
    Scores ALL intents and returns the highest-scoring one.
    Returns (intent, confidence).
    """
    lower = question.lower()
    scores: dict = {}
    for intent, keywords in _INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > 0:
            scores[intent] = score
    if not scores:
        return IntentCategory.GENERAL, 0.50
    best = max(scores, key=scores.__getitem__)
    # Normalise: max 3 hits → 0.95 confidence
    confidence = min(0.50 + scores[best] * 0.15, 0.95)
    return best, round(confidence, 2)


class ReasoningEngine:
    """
    Decides *what* to gather based on the question.
    Output feeds directly into the orchestrator's provider selection.
    """

    def __init__(self):
        self._extractor = EntityExtractor()

    def reason(self, question: str) -> ReasoningResult:
        """
        Args:
            question: Raw user question.
        Returns:
            ReasoningResult with intent, required_providers, and query.
        """
        query: CandidateQuery = self._extractor.extract(question)
        intent, confidence = _classify_intent(question)

        providers = required_providers(
            intent=intent.value,
            service_hints=query.service_hints,
        )

        explanation_parts = [f"Intent: {intent.value} (confidence={confidence:.0%})"]
        if query.resource_ids:
            explanation_parts.append(f"Explicit IDs: {', '.join(query.resource_ids)}")
        if query.service_hints:
            explanation_parts.append(f"Services detected: {', '.join(query.service_hints)}")
        if query.environment_hints:
            explanation_parts.append(f"Environments: {', '.join(query.environment_hints)}")

        result = ReasoningResult(
            intent=intent,
            required_providers=providers,
            resource_query=query,
            confidence=confidence,
            explanation=" | ".join(explanation_parts),
        )

        logger.info(
            "[ReasoningEngine] intent=%s providers=%s confidence=%.2f",
            intent.value, providers, confidence,
        )
        return result
