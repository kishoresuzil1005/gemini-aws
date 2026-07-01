import boto3
import logging

logger = logging.getLogger(__name__)


class TargetGroupDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client("elbv2", region_name=region)
            paginator = client.get_paginator("describe_target_groups")
            target_groups = []
            for page in paginator.paginate():
                for tg in page.get("TargetGroups", []):
                    load_balancers = list(tg.get("LoadBalancerArns", []))
                    target_groups.append({
                        "resource_id": tg["TargetGroupArn"],
                        "resource_type": "TargetGroup",
                        "region": region,
                        "name": tg.get("TargetGroupName"),
                        "protocol": tg.get("Protocol"),
                        "port": tg.get("Port"),
                        "target_type": tg.get("TargetType"),
                        "vpc_id": tg.get("VpcId"),
                        "load_balancers": load_balancers,
                        "health_check_protocol": tg.get("HealthCheckProtocol"),
                        "health_check_port": tg.get("HealthCheckPort"),
                        "health_check_path": tg.get("HealthCheckPath")
                    })
            return target_groups
        except Exception:
            logger.exception("Target Group discovery failed for region %s", region)
            return []
