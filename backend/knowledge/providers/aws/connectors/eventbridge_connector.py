# knowledge/providers/aws/connectors/eventbridge_connector.py
"""Connector for AWS EventBridge Documentation.

Collects structural and metadata definitions related to EventBridge.
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


class EventBridgeConnector(BaseMonitoringConnector):
    """Connector that retrieves EventBridge metadata.
    
    Discovers available event buses and fetches rules and patterns attached
    to them without collecting actual live events.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("events", region_name=self.config.region)

    def discover_definitions(self) -> List[str]:
        try:
            paginator = self.client.get_paginator("list_event_buses")
            buses = []
            for page in paginator.paginate():
                for bus in page.get("EventBuses", []):
                    buses.append(bus["Name"])
            return buses
        except (BotoCoreError, ClientError) as exc:
            raise ConnectorError(f"Failed to list EventBridge buses: {exc}")

    def fetch_metadata(self, bus_name: str) -> Dict[str, Any]:
        try:
            paginator = self.client.get_paginator("list_rules")
            rules = []
            for page in paginator.paginate(EventBusName=bus_name):
                for rule in page.get("Rules", []):
                    rules.append({
                        "name": rule.get("Name"),
                        "description": rule.get("Description"),
                        "event_pattern": rule.get("EventPattern")
                    })
            return {
                "event_bus": bus_name,
                "rules": rules
            }
        except (BotoCoreError, ClientError) as exc:
            raise FetchError(f"Failed to fetch rules for event bus {bus_name}: {exc}")

    def validate(self, raw_data: bytes) -> Any:
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No EventBridge data fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        return f"{self.config.version}|eventbridge-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="eventbridge",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported EventBridge snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
