# knowledge/rules/rule_lifecycle.py
"""Enforces state transitions for the Rule Catalog."""

import logging

from .rule_models import CanonicalRule
from .rule_exceptions import InvalidStateTransitionError

logger = logging.getLogger(__name__)

class RuleLifecycle:
    """Manages the state machine: DRAFT -> APPROVED -> PUBLISHED -> DEPRECATED -> ARCHIVED."""

    VALID_TRANSITIONS = {
        "DRAFT": ["APPROVED", "ARCHIVED"],
        "APPROVED": ["PUBLISHED", "DRAFT", "ARCHIVED"],
        "PUBLISHED": ["DEPRECATED", "ARCHIVED"],
        "DEPRECATED": ["ARCHIVED"],
        "ARCHIVED": [] # Terminal state
    }

    def transition(self, rule: CanonicalRule, new_status: str) -> None:
        """Transitions a rule to a new state if valid."""
        current_status = rule.status
        
        if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
            raise InvalidStateTransitionError(
                f"Cannot transition rule {rule.rule_id} from {current_status} to {new_status}"
            )
            
        rule.status = new_status
        logger.info(f"Rule {rule.rule_id} transitioned to {new_status}")
