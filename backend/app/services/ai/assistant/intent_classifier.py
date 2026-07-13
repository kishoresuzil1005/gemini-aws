from typing import Dict, Any

class IntentClassifier:
    """
    Production-ready intent classifier.
    Detects user intent using keyword groups and returns a confidence score.
    """

    INTENT_KEYWORDS = {
        "SECURITY": [
            "security", "secure", "insecure", "analyze", "analyse",
            "inspect", "review", "audit", "check", "vulnerability", "risk"
        ],
        "DEPENDENCY": [
            "dependency", "dependencies", "depends", "connected",
            "relationship", "upstream", "downstream"
        ],
        "BLAST_RADIUS": [
            "blast radius", "what happens if", "delete", "remove",
            "terminate", "destroy"
        ],
        "ROOT_CAUSE": [
            "root cause", "why", "failing", "failure", "broken",
            "error", "incident"
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
        msg = message.lower()
        detected_intent = "UNKNOWN"
        confidence = 0.0

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in msg:
                    detected_intent = intent
                    confidence = 0.95
                    break
            if detected_intent != "UNKNOWN":
                break

        return {
            "intent": detected_intent,
            "confidence": confidence
        