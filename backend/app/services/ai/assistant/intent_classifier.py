from typing import Dict, Any

class IntentClassifier:
    """
    Production-ready intent classifier.
    Detects user intent using keyword groups and returns a confidence score.
    """

    INTENT_KEYWORDS = {
        "HEALTH_CHECK": [
            "unhealthy", "failing", "down", "error", "slow", "status", "health"
        ],
        "COST_ANALYSIS": [
            "cost", "bill", "expensive", "spend", "budget", "pricing"
        ],
        "INFRASTRUCTURE_ANALYSIS": [
            "analyze", "architecture", "vpc", "subnet", "network", "design", "evaluate"
        ],
        "SECURITY": [
            "security", "secure", "insecure", "analyze", "analyse",
            "inspect", "review", "audit", "check", "vulnerability", "risk"
        ],
        "DEPENDENCY": [
            "dependency", "dependencies", "depends", "connected",
            "relationship", "upstream", "downstream", "breaks", "fails", "fail"
        ],
        "BLAST_RADIUS": [
            "blast radius", "what happens if", "delete", "remove",
            "terminate", "destroy"
        ],
        "ROOT_CAUSE": [
            "root cause", "why", "incident"
        ],
        "RECOMMENDATION": [
            "recommend", "recommendation", "how do i", "best practice", "improve"
        ],
        "REMEDIATION": [
            "terraform", "cloudformation", "aws cli", "fix", "repair",
            "remediate", "generate terraform", "generate cloudformation"
        ],
        "ORCHESTRATION": [
            "execute", "run", "automation", "automate", "orchestrate",
            "safely execute", "rollback"
        ],
        "DOCUMENTATION": [
            "what is", "tell me about", "documentation", "explain",
            "describe", "guide"
        ],
        "INVENTORY": [
            "inventory", "list", "show", "display", "resources", "compare"
        ]
    }

    def classify(self, message: str) -> Dict[str, Any]:
        """Classify the intent of a message.

        Returns a dict with 'intent' and 'confidence' keys. The method now scores
        all possible intents based on keyword matches and selects the intent with
        the highest confidence. This prevents early‑match issues where a generic
        intent (e.g., HEALTH_CHECK) would swallow more specific intents like
        COST_ANALYSIS.
        """
        msg = message.lower()
        best_intent = "UNKNOWN"
        best_confidence = 0.0
        for intent, keywords in self.INTENT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in msg)
            if matches:
                # Base confidence for a match, plus a flat boost per match
                # (capped at 0.15). Ties preserve earlier intents (e.g. HEALTH_CHECK).
                confidence = 0.85 + min(matches * 0.05, 0.15)
                if confidence > best_confidence:
                    best_intent = intent
                    best_confidence = confidence
        return {"intent": best_intent, "confidence": best_confidence}