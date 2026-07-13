"""
Drift Policy — Production Implementation
Defines and evaluates policies for each classification of drift.
"""
import logging
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DriftAction(str, Enum):
    IGNORE = "ignore"
    WARN = "warn"
    REPAIR = "repair"
    MISSION = "mission"  # Trigger Mission Control for remediation


class DriftPolicy:
    """
    Evaluates drift events against configured policies and returns
    the action to take for each drift classification.

    Default policy:
    - Manual Console changes -> WARN
    - Unknown drift         -> WARN
    - Terraform drift       -> IGNORE (Terraform will re-apply)
    - CloudFormation drift  -> IGNORE (CF drift detection handles it)
    - Pipeline drift        -> WARN
    """

    DEFAULT_POLICIES: Dict[str, str] = {
        "Manual": DriftAction.WARN,
        "CloudFormation": DriftAction.IGNORE,
        "Terraform": DriftAction.IGNORE,
        "Pipeline": DriftAction.WARN,
        "Unknown": DriftAction.WARN,
    }

    def __init__(self, custom_policies: Optional[Dict[str, str]] = None):
        self.policies = {**self.DEFAULT_POLICIES, **(custom_policies or {})}

    def evaluate(self, drift_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single drift event and annotates it with the action to take.

        Args:
            drift_event: Drift event, possibly already classified.

        Returns:
            drift_event with 'policy_action' and 'policy_reason' fields added.
        """
        classification = drift_event.get("classification", "Unknown")
        drift_type = drift_event.get("drift_type", "changed")
        resource_id = drift_event.get("resource_id", "unknown")

        # Critical resources (tagged as critical or production) escalate to MISSION
        tags = {}
        live_state = drift_event.get("live_state") or {}
        if isinstance(live_state, dict):
            tags = live_state.get("metadata", {}).get("tags", {}) or {}

        is_critical = any(
            v.lower() in ("true", "critical", "production", "prod")
            for k, v in tags.items()
            if k.lower() in ("critical", "environment", "env")
        )

        if is_critical and classification == "Manual":
            action = DriftAction.MISSION
            reason = f"Critical resource '{resource_id}' was manually changed — triggering Mission Control"
        elif drift_type == "removed":
            action = DriftAction.WARN
            reason = f"Resource '{resource_id}' was unexpectedly removed"
        else:
            action = self.policies.get(classification, DriftAction.WARN)
            reason = f"Policy for classification '{classification}' is '{action}'"

        drift_event["policy_action"] = action
        drift_event["policy_reason"] = reason

        logger.info(f"Drift policy: {resource_id} -> {action} ({reason})")
        return drift_event

    def evaluate_batch(self, drift_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluates a list of drift events."""
        return [self.evaluate(event) for event in drift_events]

    def get_actionable_events(self, drift_events: List[Dict[str, Any]], actions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Returns events that match specific policy actions."""
        target_actions = set(actions or [DriftAction.WARN, DriftAction.REPAIR, DriftAction.MISSION])
        return [e for e in drift_events if e.get("policy_action") in target_actions]