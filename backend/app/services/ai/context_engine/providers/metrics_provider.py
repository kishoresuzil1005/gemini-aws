"""MetricsProvider – fetches core CloudWatch performance metrics.

Uses boto3 CloudWatch ``get_metric_data`` to retrieve CPU, Memory,
Network, Disk, and Status Check metrics for the given resource.

Look-back window is configurable via ``ContextRequest.metrics_look_back``
(default 24 hours).  Resolution is 5-minute periods.
"""

import time
import logging
from datetime import timezone
from typing import Any, Dict, List

import boto3

from ..base_provider import BaseProvider
from ..common.constants import METRICS_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..common.time import look_back_range
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class MetricsProvider(BaseProvider):
    """Fetches core performance metrics from CloudWatch."""

    name       = "metrics"
    scope      = ProviderScope.DYNAMIC
    priority   = 50
    output_key = "metrics"
    cache_ttl  = TTL_DYNAMIC
    version    = "1.0"
    source     = "cloudwatch"
    enabled    = flag_enabled(METRICS_PROVIDER_ENABLED)

    def __init__(self, *, cloudwatch_service):
        super().__init__()
        self.cloudwatch_service = cloudwatch_service

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_metrics(resource.resource_id, request.metrics_look_back)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_metrics(self, resource_id: str, look_back_hours: int) -> Dict[str, Any]:
        start, end = look_back_range(look_back_hours)
        # CloudWatch requires tz-aware datetimes
        start_dt = start.replace(tzinfo=timezone.utc) if start.tzinfo is None else start
        end_dt   = end.replace(tzinfo=timezone.utc)   if end.tzinfo is None   else end
        period    = 300  # 5-minute resolution

        datapoints: Dict[str, List] = {
            "cpu_utilization":     [],
            "memory_utilization":  [],
            "network_in":          [],
            "network_out":         [],
            "disk_read_bytes":     [],
            "disk_write_bytes":    [],
            "status_check_failed": [],
        }

        # Determine dimension based on resource type
        if resource_id.startswith("i-"):
            namespace  = "AWS/EC2"
            dimensions = [{"Name": "InstanceId", "Value": resource_id}]
            metric_queries = self._ec2_metric_queries(resource_id)
        elif resource_id.startswith("db-") or resource_id.startswith("cluster:"):
            namespace  = "AWS/RDS"
            dimensions = [{"Name": "DBInstanceIdentifier", "Value": resource_id}]
            metric_queries = self._rds_metric_queries(resource_id)
        else:
            # Generic – try EC2 style
            namespace  = "AWS/EC2"
            dimensions = [{"Name": "InstanceId", "Value": resource_id}]
            metric_queries = self._ec2_metric_queries(resource_id)

        try:
            response = self.cloudwatch_service.get_metric_data(
                metric_queries=metric_queries,
                start_time=start_dt,
                end_time=end_dt,
            )

            for result in response.get("MetricDataResults", []):
                label = result.get("Id", "")
                timestamps = result.get("Timestamps", [])
                values     = result.get("Values", [])
                points = [
                    {"timestamp": ts.isoformat(), "value": round(v, 4)}
                    for ts, v in zip(timestamps, values)
                ]
                if label in datapoints:
                    datapoints[label] = sorted(points, key=lambda x: x["timestamp"])

        except Exception as exc:
            logger.warning("MetricsProvider cloudwatch failed for %s: %s", resource_id, exc)

        # Compute summary
        cpu_vals  = [p["value"] for p in datapoints["cpu_utilization"]]
        mem_vals  = [p["value"] for p in datapoints["memory_utilization"]]

        return {
            "look_back_hours": look_back_hours,
            "period_seconds":  period,
            "datapoints":      datapoints,
            "summary": {
                "avg_cpu":    round(sum(cpu_vals) / len(cpu_vals), 2) if cpu_vals else 0.0,
                "avg_memory": round(sum(mem_vals) / len(mem_vals), 2) if mem_vals else 0.0,
            },
        }

    # ------------------------------------------------------------------
    #  Metric query builders
    # ------------------------------------------------------------------

    def _ec2_metric_queries(self, instance_id: str) -> List[Dict]:
        dim = [{"Name": "InstanceId", "Value": instance_id}]
        return [
            self._mq("cpu_utilization",     "AWS/EC2", "CPUUtilization",            dim),
            self._mq("network_in",          "AWS/EC2", "NetworkIn",                 dim),
            self._mq("network_out",         "AWS/EC2", "NetworkOut",                dim),
            self._mq("disk_read_bytes",     "AWS/EC2", "DiskReadBytes",             dim),
            self._mq("disk_write_bytes",    "AWS/EC2", "DiskWriteBytes",            dim),
            self._mq("status_check_failed", "AWS/EC2", "StatusCheckFailed",         dim),
            # Memory requires CloudWatch Agent (CWAgent namespace)
            self._mq("memory_utilization", "CWAgent", "mem_used_percent",
                     [{"Name": "InstanceId", "Value": instance_id}]),
        ]

    def _rds_metric_queries(self, db_id: str) -> List[Dict]:
        dim = [{"Name": "DBInstanceIdentifier", "Value": db_id}]
        return [
            self._mq("cpu_utilization",    "AWS/RDS", "CPUUtilization",    dim),
            self._mq("network_in",         "AWS/RDS", "NetworkReceiveThroughput", dim),
            self._mq("network_out",        "AWS/RDS", "NetworkTransmitThroughput", dim),
            self._mq("disk_read_bytes",    "AWS/RDS", "ReadIOPS",          dim),
            self._mq("disk_write_bytes",   "AWS/RDS", "WriteIOPS",         dim),
            self._mq("memory_utilization", "AWS/RDS", "FreeableMemory",    dim),
        ]

    def _mq(self, metric_id: str, namespace: str, metric_name: str, dimensions: List[Dict]) -> Dict:
        return {
            "Id":         metric_id,
            "MetricStat": {
                "Metric": {
                    "Namespace":  namespace,
                    "MetricName": metric_name,
                    "Dimensions": dimensions,
                },
                "Period": 300,
                "Stat":   "Average",
            },
            "ReturnData": True,
        }
