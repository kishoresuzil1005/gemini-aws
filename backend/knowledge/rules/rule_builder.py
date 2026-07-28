# knowledge/rules/rule_builder.py
"""Builds and compiles Canonical Rules from raw M7 output."""

import logging
from typing import List

from .rule_models import CanonicalRule
from .rule_classifier import RuleClassifier
from .rule_validator import RuleValidator

logger = logging.getLogger(__name__)

class RuleBuilder:
    """Ingests raw rules and validates them before catalog inclusion."""

    def __init__(self):
        self.classifier = RuleClassifier()
        self.validator = RuleValidator()

    def build(self, raw_rules: List[CanonicalRule]) -> List[CanonicalRule]:
        """Validates incoming rules and enforces taxonomic classification."""
        for rule in raw_rules:
            # Enforce category mapping
            rule.category = self.classifier.classify(rule.category)
            
        valid_rules = self.validator.validate(raw_rules)
        logger.info(f"Rule builder processed {len(valid_rules)} valid rules.")
        return valid_rules
