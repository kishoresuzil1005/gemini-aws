# knowledge/providers/aws/connectors/trusted_advisor_connector.py
"""Connector for AWS Trusted Advisor Documentation.

Collects metadata on checks across Cost Optimization, Security, Performance,
and Fault Tolerance.
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


class TrustedAdvisorConnector(BaseMonitoringConnector):
    """Connector that retrieves Trusted Advisor check definitions.
    
    Access to the Support API requires an Enterprise or Business Support plan.
    Extracts check IDs, names, and categories without executing them.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("support", region_name="us-east-1") # Support API is in us-east-1

    def discover_definitions(self) -> List[str]:
        """Discover check IDs by fetching all available checks."""
        try:
            # We fetch all check metadata at once since there's no paginator and it's a small list.
            resp = self.client.describe_trusted_advisor_checks(language="en")
            # We return a single identifier 'all_checks' as discover_definitions returns a list of things to fetch,
            # but since we already got them all, we can just cache them on the instance to avoid double fetching.
            self._cached_checks = resp.get("checks", [])
            return ["all_checks"]
        except (BotoCoreError, ClientError) as exc:
            logger.warning(f"Could not access Support API: {exc}")
            # Fallback mock for offline knowledge extraction
            return ["mock_checks"]

    def fetch_metadata(self, definition: str) -> Dict[str, Any]:
        """Format the cached check metadata."""
        if definition == "all_checks" and hasattr(self, "_cached_checks"):
            return {
                "category": "all",
                "checks": [
                    {
                        "check_id": check.get("id"),
                        "check_name": check.get("name"),
                        "category": check.get("category"),
                        "description": check.get("description")
                    }
                    for check in self._cached_checks
                ]
            }
        
        # Fallback return for mock
        return {
            "category": "mock",
            "checks": [
                {
                    "check_id": "mock_id_1",
                    "check_name": "Mock Security Check",
                    "category": "security",
                    "description": "Mock description for offline testing."
                }
            ]
        }

    def validate(self, raw_data: bytes) -> Any:
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No Trusted Advisor data fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        return f"{self.config.version}|trusted-advisor-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="trusted_advisor",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported Trusted Advisor snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
