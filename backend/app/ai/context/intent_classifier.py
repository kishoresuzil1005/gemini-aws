"""
CloudOps AI Intent Classifier

Converts a natural language query into a structured IntentResult.

This module does NOT call Ollama.
It is deterministic and very fast.

LLM reasoning happens later.
"""

from __future__ import annotations

import re
from typing import List

from app.ai.intents import Intent
from app.ai.context.models import (
    IntentResult,
    CloudResource,
    ResourceType,
)

from app.ai.context.patterns import (
    INTENT_PATTERNS,
    RESOURCE_PATTERNS,
    ACTION_PATTERNS,
)


class IntentClassifier:

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def classify(self, query: str) -> IntentResult:

        text = query.lower().strip()

        intent = self._detect_intent(text)

        action = self._detect_action(text)

        resources = self._extract_resources(text)

        confidence = self._calculate_confidence(
            intent,
            resources
        )

        return IntentResult(
            intent=intent,
            confidence=confidence,
            resources=resources,
            action=action,
            original_query=query,
        )

    # ---------------------------------------------------------

    def _detect_intent(self, text: str) -> Intent:

        scores = {}

        for intent_name, keywords in INTENT_PATTERNS.items():

            score = 0

            for keyword in keywords:

                if keyword in text:
                    score += 1

            scores[intent_name] = score

        if not scores:
            return Intent.GENERAL

        best = max(scores, key=scores.get)

        if scores[best] == 0:
            return Intent.GENERAL

        try:
            return Intent(best)
        except Exception:
            return Intent.GENERAL

    # ---------------------------------------------------------

    def _detect_action(self, text: str):

        for action, keywords in ACTION_PATTERNS.items():

            for keyword in keywords:

                if keyword in text:
                    return action

        return None

    # ---------------------------------------------------------

    def _extract_resources(
        self,
        text: str,
    ) -> List[CloudResource]:

        resources = []

        for resource_name, keywords in RESOURCE_PATTERNS.items():

            for keyword in keywords:

                if keyword in text:

                    try:

                        resource_type = ResourceType(resource_name)

                    except Exception:

                        resource_type = ResourceType.UNKNOWN

                    resources.append(
                        CloudResource(
                            resource_type=resource_type,
                            name=self._extract_name(
                                keyword,
                                text,
                            ),
                        )
                    )

                    break

        return resources

    # ---------------------------------------------------------

    def _extract_name(
        self,
        keyword: str,
        text: str,
    ):

        pattern = rf"{keyword}\s+([a-zA-Z0-9\-_.]+)"

        match = re.search(
            pattern,
            text,
        )

        if match:
            return match.group(1)

        return None

    # ---------------------------------------------------------

    def _calculate_confidence(
        self,
        intent,
        resources,
    ) -> float:

        confidence = 0.50

        if intent != Intent.GENERAL:
            confidence += 0.25

        if len(resources):
            confidence += 0.20

        if len(resources) > 1:
            confidence += 0.05

        return min(confidence, 1.0)
