# knowledge/rules/rule_classifier.py
"""Maps raw rules into standardized categories."""

import logging

logger = logging.getLogger(__name__)

class RuleClassifier:
    """Strictly categorizes rules into the 9 major pillars."""
    
    VALID_CATEGORIES = {
        "Security", "Cost Optimization", "Performance", "Reliability",
        "Architecture", "Operations", "Compliance", "Governance", "Sustainability"
    }

    def classify(self, raw_category: str) -> str:
        """Map a raw string to the official taxonomy."""
        # Simple exact match for now
        for valid in self.VALID_CATEGORIES:
            if raw_category.lower() == valid.lower():
                return valid
                
        logger.warning(f"Unmapped rule category '{raw_category}'. Defaulting to 'Governance'.")
        return "Governance"
