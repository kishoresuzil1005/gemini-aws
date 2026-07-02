"""
CloudOps AI Router

This module is responsible for routing user requests into the
Cloud Context Builder pipeline.
"""

from app.ai.context.intent_classifier import IntentClassifier


class AIRouter:

    def __init__(self):
        self.intent_classifier = IntentClassifier()

    def classify(self, query: str):
        """
        Classify a natural language query.

        Returns
        -------
        IntentResult
        """
        return self.intent_classifier.classify(query)


# Singleton
router = AIRouter()
