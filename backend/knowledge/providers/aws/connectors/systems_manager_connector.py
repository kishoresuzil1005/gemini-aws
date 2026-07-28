# knowledge/providers/aws/connectors/systems_manager_connector.py
"""Connector for AWS Systems Manager Documentation.

Collects metadata on Automation Documents, Runbooks, and Maintenance Windows.
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


class SystemsManagerConnector(BaseMonitoringConnector):
    """Connector that retrieves SSM Document (Runbook) definitions."""

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self.client = boto3.client("ssm", region_name=self.config.region)

    def discover_definitions(self) -> List[str]:
        """Discover available public/AWS-owned SSM documents."""
        try:
            paginator = self.client.get_paginator("list_documents")
            docs = []
            # We filter by AWS owned documents to get official runbooks
            for page in paginator.paginate(DocumentFilterList=[{'key': 'Owner', 'value': 'Amazon'}]):
                for doc in page.get("DocumentIdentifiers", []):
                    if doc.get("DocumentType") in ["Automation", "Command"]:
                        docs.append(doc["Name"])
            return docs
        except (BotoCoreError, ClientError) as exc:
            raise ConnectorError(f"Failed to list SSM documents: {exc}")

    def fetch_metadata(self, document_name: str) -> Dict[str, Any]:
        """Fetch the schema/parameters for a specific SSM document."""
        try:
            resp = self.client.describe_document(Name=document_name)
            doc_info = resp.get("Document", {})
            return {
                "document_name": doc_info.get("Name"),
                "document_type": doc_info.get("DocumentType"),
                "description": doc_info.get("Description"),
                "parameters": doc_info.get("Parameters", []),
                "document_version": doc_info.get("DocumentVersion")
            }
        except (BotoCoreError, ClientError) as exc:
            raise FetchError(f"Failed to describe SSM document {document_name}: {exc}")

    def validate(self, raw_data: bytes) -> Any:
        parsed = json.loads(raw_data)
        if not parsed:
            raise ValidationError("No Systems Manager data fetched.")
        return parsed

    def version(self, parsed_data: Any) -> str:
        return f"{self.config.version}|ssm-v1"

    def snapshot(self, parsed_data: Any, version: str) -> str:
        from .monitoring_snapshot_manager import MonitoringSnapshotManager
        manager = MonitoringSnapshotManager(self.config)
        return manager.save_snapshot(
            json.dumps(parsed_data).encode("utf-8"),
            connector_name="systems_manager",
            version=version
        )

    def export(self, snapshot_path: str) -> None:
        logger.info("Exported Systems Manager snapshot to %s", snapshot_path)

    def shutdown(self) -> None:
        self.client.close()
