"""CloudTrail Service — Production"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class CloudtrailService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("cloudtrail", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        resp = self._client().describe_trails(includeShadowTrails=True)
        trails = []
        for trail in resp.get("trailList", []):
            try:
                status = self._client().get_trail_status(Name=trail["TrailARN"])
                is_logging = status.get("IsLogging", False)
                latest_delivery = str(status.get("LatestDeliveryTime", ""))
                latest_error = status.get("LatestDeliveryError", "")
            except Exception:
                is_logging = False
                latest_delivery = ""
                latest_error = ""

            trails.append({
                "resource_id": trail.get("TrailARN", trail["Name"]),
                "resource_type": "CloudTrail",
                "name": trail.get("Name"),
                "region": self.region,
                "status": "logging" if is_logging else "not_logging",
                "metadata": {
                    "s3_bucket": trail.get("S3BucketName"),
                    "s3_key_prefix": trail.get("S3KeyPrefix"),
                    "is_multi_region": trail.get("IsMultiRegionTrail"),
                    "include_global_service_events": trail.get("IncludeGlobalServiceEvents"),
                    "log_file_validation": trail.get("LogFileValidationEnabled"),
                    "cloud_watch_logs_arn": trail.get("CloudWatchLogsLogGroupArn"),
                    "cloud_watch_logs_role": trail.get("CloudWatchLogsRoleArn"),
                    "kms_key_id": trail.get("KMSKeyId"),
                    "is_organization_trail": trail.get("IsOrganizationTrail"),
                    "latest_delivery_time": latest_delivery,
                    "latest_delivery_error": latest_error,
                },
            })
        return trails

    def get(self, trail_name: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self._client().get_trail(Name=trail_name)
            return resp.get("Trail")
        except Exception as e:
            logger.error(f"get_trail failed: {e}")
            return None

    def lookup_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        attribute_key: Optional[str] = None,
        attribute_value: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"MaxResults": max_results}
        if start_time:
            kwargs["StartTime"] = start_time
        if end_time:
            kwargs["EndTime"] = end_time
        if attribute_key and attribute_value:
            kwargs["LookupAttributes"] = [{"AttributeKey": attribute_key, "AttributeValue": attribute_value}]
        resp = self._client().lookup_events(**kwargs)
        return resp.get("Events", [])

    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        end = datetime.utcnow()
        start = end - timedelta(hours=hours)
        return self.lookup_events(start_time=start, end_time=end)

    def start_logging(self, trail_name: str) -> Dict[str, Any]:
        self._client().start_logging(Name=trail_name)
        return {"status": "logging_started", "trail": trail_name}

    def stop_logging(self, trail_name: str) -> Dict[str, Any]:
        self._client().stop_logging(Name=trail_name)
        return {"status": "logging_stopped", "trail": trail_name}
