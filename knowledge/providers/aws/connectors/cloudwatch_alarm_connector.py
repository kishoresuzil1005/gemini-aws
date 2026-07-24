# knowledge/providers/aws/connectors/cloudwatch_alarm_connector.py
"""Connector for AWS CloudWatch Alarm Reference.

Collects structural and metadata definitions related to CloudWatch Alarms.
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


class CloudWatchAlarmConnector(BaseMonitoringConnector):
    """Connector that retrieves CloudWatch Alarm metadata structures.

    This connector currently fetches metadata based on existing alarms to infer
    supported metrics and comparison operators, though a full reference might
    pull static documentation.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("cloudwatch", region_name=self.config.region)

    def discover_definitions(self) -> List[str]:
        # We define predefined logical sections or static identifiers for alarms.
        return ["MetricAlarms", "CompositeAlarms"]

    def fetch_metadata(self, definition: str) -> Dict[str, Any]:
        try:
            paginator = self.client.get_paginator("describe_alarms")
            alarms_info = []

            for page in paginator.paginate(AlarmTypes=[definition]):
                for alarm in page.get(definition, []):
                    # We only extract schema information (states, types), not live values
                    alarms_info.append({
                        "alarm_name": alarm.get("AlarmName"),
                        "comparison_operator": alarm.get("ComparisonOperator"),
                        "evaluation_periods": alarm.get("EvaluationPeriods"),
                        "metric_name": alarm.get("MetricName"),
                        "namespace": alarm.get("Namespace"),
                        "statistic": alarm.get("Statistic"),
                        "treat_missing_data": alarm.get("TreatMissingData")
                    })

            return {
                "definition": definition,
                "alarms_schema": alarms_info
            }
        except (BotoCoreError, ClientError) as exc:
            raise FetchError(f"Failed to fetch metadata for {definition}: {exc}")

    def validate(self, raw_data: bytes) -> Any:
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No alarm definitions fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        return f"{self.config.version}|alarms-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="cloudwatch_alarms",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported CloudWatch Alarms snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
