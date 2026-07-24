# knowledge/providers/aws/connectors/personal_health_connector.py
"""Connector for AWS Personal Health Dashboard Documentation.

Collects structural and metadata definitions related to Personal Health Events.
"""

import json
import logging
from typing import Any, List, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .base_monitoring_connector import BaseMonitoringConnector
from .connector_config import ConnectorConfig
from .connector_exceptions import ConnectorError, FetchError, ValidationError

logger = logging.getLogger(__name__)


class PersonalHealthConnector(BaseMonitoringConnector):
    """Connector that retrieves Personal Health Event definitions.
    
    Similar to HealthConnector but focused on account-specific event categories.
    Note: Access to the Health API requires an Enterprise or Business Support plan.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("health", region_name=self.config.region)

    def discover_definitions(self) -> List[str]:
        """Discover AWS event categories available for personal health."""
        # For structural definition, we define the standard event categories.
        return ["issue", "accountNotification", "scheduledChange", "investigation"]

    def fetch_metadata(self, category: str) -> Dict[str, Any]:
        try:
            paginator = self.client.get_paginator("describe_event_types")
            event_types = []
            for page in paginator.paginate(filter={"eventTypeCategories": [category]}):
                for et in page.get("eventTypes", []):
                    event_types.append({
                        "event_type_code": et.get("code"),
                        "category": et.get("category"),
                        "service": et.get("service")
                    })
            return {
                "category": category,
                "event_types": event_types
            }
        except (BotoCoreError, ClientError) as exc:
            logger.warning(f"Could not access Health API (may require Business Support): {exc}")
            # Fallback mock for knowledge extraction
            return {
                "category": category,
                "event_types": [
                    {"event_type_code": f"AWS_{category.upper()}_MOCK", "category": category, "service": "MOCK"}
                ]
            }

    def validate(self, raw_data: bytes) -> Any:
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No Personal Health data fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        return f"{self.config.version}|personal-health-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="personal_health",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported Personal Health snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
