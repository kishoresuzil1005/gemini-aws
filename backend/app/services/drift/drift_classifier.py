"""
Drift Classifier — Production Implementation
Classifies the origin of detected drift: Terraform, CloudFormation, Manual, Pipeline, or Unknown.
"""
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DriftClassifier:
    """
    Analyzes drift events and classifies them by probable root cause mechanism.
    Uses CloudTrail event patterns, resource tags, and metadata heuristics.
    """

    # Tag patterns that indicate managed resources
    TERRAFORM_TAGS = ["terraform", "tf-managed", "managed-by=terraform"]
    CLOUDFORMATION_TAGS = ["aws:cloudformation:stack-name", "aws:cloudformation:logical-id"]
    PIPELINE_TAGS = ["ci-pipeline", "github-actions", "codepipeline", "jenkins"]

    # CloudTrail event sources that indicate manual console changes
    CONSOLE_EVENT_SOURCES = [
        "signin.amazonaws.com",
        "console.amazonaws.com",
    ]

    def classify(self, drift_event: Dict[str, Any], cloudtrail_events: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Classifies a single drift event.

        Args:
            drift_event: A single entry from DriftEngine output (added/removed/changed).
            cloudtrail_events: Optional list of recent CloudTrail events for this resource.

        Returns:
            Drift event enriched with classification info.
        """
        classification = "Unknown"
        confidence = 0.0
        evidence = []

        resource_id = drift_event.get("resource_id", "")
        live_state = drift_event.get("live_state") or {}
        stored_state = drift_event.get("stored_state") or {}
        tags = live_state.get("metadata", {}).get("tags", {}) or stored_state.get("metadata", {}).get("tags", {})

        # ─── Tag-based Classification ────────────────────────────────────────────
        tag_keys = [k.lower() for k in tags.keys()]
        tag_values = [str(v).lower() for v in tags.values()]

        if any(t in tag_keys for t in ["aws:cloudformation:stack-name", "aws:cloudformation:logical-id"]):
            classification = "CloudFormation"
            confidence = 0.95
            evidence.append("resource has CloudFormation managed tags")

        elif any(t in tag_keys for t in ["terraform", "tf-managed"]) or any("terraform" in v for v in tag_values):
            classification = "Terraform"
            confidence = 0.9
            evidence.append("resource has Terraform managed tags")

        elif any(t in tag_keys for t in ["ci-pipeline", "github-actions", "codepipeline", "jenkins"]):
            classification = "Pipeline"
            confidence = 0.85
            evidence.append("resource has CI/CD pipeline tags")

        # ─── CloudTrail-based Classification ─────────────────────────────────────
        if cloudtrail_events:
            for event in cloudtrail_events:
                event_source = event.get("EventSource", "")
                user_type = event.get("UserIdentity", {}).get("type", "")
                username = event.get("Username", "")

                if event_source in self.CONSOLE_EVENT_SOURCES or "console" in event_source.lower():
                    classification = "Manual"
                    confidence = max(confidence, 0.95)
                    evidence.append(f"CloudTrail shows console access by {username}")
                    break

                if "terraform" in username.lower() or "tf-" in username.lower():
                    classification = "Terraform"
                    confidence = max(confidence, 0.98)
                    evidence.append(f"CloudTrail shows Terraform identity: {username}")
                    break

                if user_type == "AssumedRole":
                    role_name = event.get("UserIdentity", {}).get("Arn", "")
                    if "pipeline" in role_name.lower() or "cicd" in role_name.lower():
                        classification = "Pipeline"
                        confidence = max(confidence, 0.9)
                        evidence.append(f"CloudTrail shows pipeline role: {role_name}")
                        break

        drift_event["classification"] = classification
        drift_event["classification_confidence"] = confidence
        drift_event["classification_evidence"] = evidence

        logger.debug(f"Drift classified: {resource_id} -> {classification} (confidence={confidence:.0%})")
        return drift_event

    def classify_batch(self, drift_events: List[Dict[str, Any]], cloudtrail_events: Optional[Dict[str, List]] = None) -> List[Dict[str, Any]]:
        """
        Classifies multiple drift events.

        Args:
            drift_events: List from DriftEngine output.
            cloudtrail_events: Map of resource_id -> list of CloudTrail events.
        """
        classified = []
        for event in drift_events:
            resource_id = event.get("resource_id", "")
            ct_events = (cloudtrail_events or {}).get(resource_id, [])
            classified.append(self.classify(event, cloudtrail_events=ct_events))
        return classified