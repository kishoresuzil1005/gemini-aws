# knowledge/rules/rule_validator.py
"""Enforces schema consistency and required properties for Rules."""

import logging
from typing import List

from .rule_models import CanonicalRule
from .rule_exceptions import RuleValidationError

logger = logging.getLogger(__name__)

class RuleValidator:
    """Validates rules before they can enter the APPROVED state."""

    def validate(self, rules: List[CanonicalRule]) -> List[CanonicalRule]:
        """Validates incoming rules, discarding invalid ones."""
        valid_rules = []
        for rule in rules:
            try:
                if not rule.rule_id:
                    raise ValueError("Missing rule_id")
                if not rule.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"):
                    raise ValueError(f"Invalid severity: {rule.severity}")
                if not rule.category:
                    raise ValueError("Missing category")
                
                valid_rules.append(rule)
            except Exception as exc:
                logger.error("Rule validation failed for rule %s: %s", getattr(rule, 'rule_id', 'UNKNOWN'), exc)
                
        return valid_rules
