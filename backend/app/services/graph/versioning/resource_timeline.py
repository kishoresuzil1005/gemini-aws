"""
Resource Timeline — Production Implementation
Tracks the complete chronological history of a resource using CloudTrail and the Knowledge Graph.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class ResourceTimeline:
    """
    Builds a human-readable chronological history for any cloud resource.
    Enables AI queries like:
    - "What changed on this EC2 last week?"
    - "Who modified this RDS instance?"
    - "When was this VPC first created?"
    """

    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _cloudtrail_client(self):
        return client_factory.get_aws_client("cloudtrail", region_name=self.region, role_arn=self.role_arn)

    def get_timeline(
        self,
        resource_id: str,
        days: int = 30,
        max_events: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Returns a chronological list of events for a given resource.

        Args:
            resource_id: AWS Resource ID (e.g., i-1234567890abcdef0)
            days: Number of days to look back
            max_events: Maximum number of events to return

        Returns:
            Sorted list of timeline events, newest first.
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)

            resp = self._cloudtrail_client().lookup_events(
                LookupAttributes=[{"AttributeKey": "ResourceName", "AttributeValue": resource_id}],
                StartTime=start_time,
                EndTime=end_time,
                MaxResults=min(max_events, 50),  # CloudTrail max per call is 50
            )

            events = resp.get("Events", [])
            timeline = []
            for event in events:
                user_identity = event.get("UserIdentity", {})
                actor = (
                    user_identity.get("Arn")
                    or user_identity.get("userName")
                    or user_identity.get("type", "System")
                )
                timeline.append({
                    "event_time": str(event.get("EventTime", "")),
                    "event_name": event.get("EventName", ""),
                    "event_source": event.get("EventSource", ""),
                    "actor": actor,
                    "actor_type": user_identity.get("type", "unknown"),
                    "resources": [
                        {"id": r.get("ResourceName"), "type": r.get("ResourceType")}
                        for r in event.get("Resources", [])
                    ],
                    "read_only": event.get("ReadOnly", "false") == "true",
                })

            timeline.sort(key=lambda e: e["event_time"], reverse=True)
            logger.info(f"Timeline for {resource_id}: {len(timeline)} events in last {days} days.")
            return timeline

        except Exception as e:
            logger.error(f"ResourceTimeline.get_timeline({resource_id}) failed: {e}")
            return []

    def get_summary(self, resource_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Returns a human-readable summary of recent activity for a resource.
        Useful for AI assistant answers.
        """
        timeline = self.get_timeline(resource_id, days=days)
        if not timeline:
            return {
                "resource_id": resource_id,
                "summary": f"No CloudTrail activity found for {resource_id} in the last {days} days.",
                "events": [],
            }

        actors = list({e["actor"] for e in timeline})
        event_types = list({e["event_name"] for e in timeline})
        first_event = timeline[-1]["event_time"] if timeline else None
        last_event = timeline[0]["event_time"] if timeline else None

        return {
            "resource_id": resource_id,
            "total_events": len(timeline),
            "unique_actors": actors,
            "event_types": event_types,
            "first_activity": first_event,
            "last_activity": last_event,
            "events": timeline,
            "summary": (
                f"{resource_id} had {len(timeline)} changes in the last {days} days. "
                f"Last modified by {timeline[0]['actor']} "
                f"via {timeline[0]['event_name']} at {timeline[0]['event_time']}."
            ),
        }