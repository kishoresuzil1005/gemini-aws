"""
Drift Root Cause — Production Implementation
Traces the root cause of detected drift using CloudTrail API.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class DriftRootCause:
    """
    Traces infrastructure drift back to its origin using CloudTrail events.
    Determines who, what, when, and how a resource was changed.
    """

    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _cloudtrail_client(self):
        return client_factory.get_aws_client("cloudtrail", region_name=self.region, role_arn=self.role_arn)

    def find_root_cause(self, drift_event: Dict[str, Any], lookback_hours: int = 72) -> Dict[str, Any]:
        """
        Enriches a drift event with CloudTrail root cause information.

        Args:
            drift_event: A drift event from DriftEngine / DriftClassifier.
            lookback_hours: How many hours back to search CloudTrail.

        Returns:
            drift_event enriched with root_cause block.
        """
        resource_id = drift_event.get("resource_id", "")
        if not resource_id:
            drift_event["root_cause"] = {"error": "no resource_id provided"}
            return drift_event

        events = self._lookup_cloudtrail_events(resource_id, lookback_hours)

        if not events:
            drift_event["root_cause"] = {
                "found": False,
                "message": "No CloudTrail events found in the lookback window",
                "resource_id": resource_id,
                "lookback_hours": lookback_hours,
            }
            return drift_event

        # The most recent event is the likely root cause
        triggering_event = events[0]
        user_identity = triggering_event.get("UserIdentity", {})
        actor = user_identity.get("Arn") or user_identity.get("userName") or "unknown"
        actor_type = user_identity.get("type", "unknown")
        event_time = triggering_event.get("EventTime")
        event_name = triggering_event.get("EventName", "")
        event_source = triggering_event.get("EventSource", "")

        drift_event["root_cause"] = {
            "found": True,
            "resource_id": resource_id,
            "triggering_event": event_name,
            "event_source": event_source,
            "actor": actor,
            "actor_type": actor_type,
            "event_time": str(event_time) if event_time else None,
            "total_events_found": len(events),
            "recent_events": [
                {
                    "event_name": e.get("EventName"),
                    "event_time": str(e.get("EventTime", "")),
                    "actor": (e.get("UserIdentity") or {}).get("Arn") or (e.get("UserIdentity") or {}).get("userName"),
                    "source": e.get("EventSource"),
                }
                for e in events[:5]
            ],
        }

        logger.info(f"Root cause for {resource_id}: {event_name} by {actor} at {event_time}")
        return drift_event

    def find_root_cause_batch(self, drift_events: List[Dict[str, Any]], lookback_hours: int = 72) -> List[Dict[str, Any]]:
        """Enriches multiple drift events with root cause data."""
        return [self.find_root_cause(event, lookback_hours=lookback_hours) for event in drift_events]

    def _lookup_cloudtrail_events(self, resource_id: str, lookback_hours: int = 72) -> List[Dict[str, Any]]:
        """Queries CloudTrail for events related to a specific resource ID."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=lookback_hours)

            resp = self._cloudtrail_client().lookup_events(
                LookupAttributes=[{"AttributeKey": "ResourceName", "AttributeValue": resource_id}],
                StartTime=start_time,
                EndTime=end_time,
                MaxResults=20,
            )
            events = resp.get("Events", [])
            logger.debug(f"CloudTrail lookup for {resource_id}: {len(events)} events found.")
            return events
        except Exception as e:
            logger.warning(f"CloudTrail lookup failed for {resource_id}: {e}")
            return []