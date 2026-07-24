# knowledge/providers/aws/connectors/cloudwatch_metrics_connector.py
"""Connector for AWS CloudWatch Metrics Reference.

Collects official CloudWatch metric metadata such as Namespaces, Metric Names,
Dimensions, and Supported Statistics without executing queries or retrieving
live time-series data.
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


class CloudWatchMetricsConnector(BaseMonitoringConnector):
    """Connector that retrieves CloudWatch Metric metadata.

    Discovers available namespaces and fetches metric schemas for each.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("cloudwatch", region_name=self.config.region)

    def discover_definitions(self) -> List[str]:
        """Discover active namespaces in the account by listing metrics.
        Note: This only discovers namespaces with active metrics. For a complete
        offline reference, this would ideally parse AWS documentation. In this
        implementation, we use ListMetrics to extract structural metadata.
        """
        try:
            paginator = self.client.get_paginator("list_metrics")
            namespaces = set()
            # To avoid iterating millions of metrics, we could rely on documentation.
            # Here we demonstrate API-driven schema extraction limited to namespaces.
            for page in paginator.paginate():
                for metric in page.get("Metrics", []):
                    namespaces.add(metric["Namespace"])
            return list(namespaces)
        except (BotoCoreError, ClientError) as exc:
            raise ConnectorError(f"Failed to list CloudWatch metrics namespaces: {exc}")

    def fetch_metadata(self, namespace: str) -> Dict[str, Any]:
        """Fetch metric schemas for a specific namespace.
        Extracts Metric Name, Dimensions, and implicit structure.
        """
        try:
            paginator = self.client.get_paginator("list_metrics")
            metrics_dict: Dict[str, dict] = {}
            for page in paginator.paginate(Namespace=namespace):
                for m in page.get("Metrics", []):
                    name = m["MetricName"]
                    dimensions = [d["Name"] for d in m.get("Dimensions", [])]
                    
                    if name not in metrics_dict:
                        metrics_dict[name] = {
                            "metric_name": name,
                            "namespace": namespace,
                            "dimensions": set(dimensions),
                            "supported_statistics": ["Average", "Sum", "Minimum", "Maximum", "SampleCount"],
                        }
                    else:
                        metrics_dict[name]["dimensions"].update(dimensions)
                        
            # Convert sets to lists for JSON serialization
            metrics_list = []
            for name, data in metrics_dict.items():
                metrics_list.append({
                    "metric_name": name,
                    "namespace": data["namespace"],
                    "dimensions": [{"name": d} for d in data["dimensions"]],
                    "supported_statistics": [{"name": s} for s in data["supported_statistics"]]
                })
                
            return {
                "namespace": namespace,
                "metrics": metrics_list
            }
        except (BotoCoreError, ClientError) as exc:
            raise FetchError(f"Failed to fetch metric metadata for {namespace}: {exc}")

    def validate(self, raw_data: bytes) -> Any:
        """Validate the returned JSON data.
        """
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No metrics data fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        # Boto3 doesn't surface a direct schema version for CloudWatch namespaces.
        # Use a fixed version or API version.
        return f"{self.config.version}|cloudwatch-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="cloudwatch_metrics",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported CloudWatch Metrics snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
