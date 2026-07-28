# knowledge/providers/aws/connectors/health_connector.py
"""Connector for AWS Health API Documentation.

Collects structural and metadata definitions related to AWS Health Events.
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


class HealthConnector(BaseMonitoringConnector):
    """Connector that retrieves AWS Health Event definitions.
    
    Discovers available event types without collecting live incident data.
    Note: Access to the Health API requires an Enterprise or Business Support plan.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("health", region_name=self.config.region)

    def discover_definitions(self) -> List[str]:
        """Discover AWS services that have health event definitions."""
        try:
            # Using describe_event_types to fetch structural data
            paginator = self.client.get_paginator("describe_event_types")
            services = set()
            for page in paginator.paginate():
                for event_type in page.get("eventTypes", []):
                    services.add(event_type["service"])
            return list(services)
        except (BotoCoreError, ClientError) as exc:
            logger.warning(f"Could not access Health API (may require Business Support): {exc}")
            # Fallback for knowledge extraction
            return ["EC2", "RDS", "S3"]

    def fetch_metadata(self, service: str) -> Dict[str, Any]:
        try:
            paginator = self.client.get_paginator("describe_event_types")
            event_types = []
            for page in paginator.paginate(filter={"services": [service]}):
                for et in page.get("eventTypes", []):
                    event_types.append({
                        "event_type_code": et.get("code"),
                        "category": et.get("category"),
                        "service": et.get("service")
                    })
            return {
                "service": service,
                "event_types": event_types
            }
        except (BotoCoreError, ClientError) as exc:
            raise FetchError(f"Failed to fetch health event types for {service}: {exc}")

    def validate(self, raw_data: bytes) -> Any:
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No AWS Health data fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        return f"{self.config.version}|health-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="health",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported AWS Health snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
