import boto3
import logging

logger = logging.getLogger(__name__)


class ALBDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client("elbv2", region_name=region)
            paginator = client.get_paginator("describe_load_balancers")
            lbs = []
            for page in paginator.paginate():
                for lb in page.get("LoadBalancers", []):
                    lbs.append({
                        "resource_id": lb["LoadBalancerArn"],
                        "resource_type": "ALB",
                        "region": region,
                        "name": lb["LoadBalancerName"],
                        "dns_name": lb.get("DNSName"),
                        "scheme": lb.get("Scheme"),
                        "vpc_id": lb.get("VpcId"),
                        "state": lb.get("State", {}).get("Code")
                    })
            return lbs
        except Exception:
            logger.exception("ALB discovery failed for region %s", region)
            return []
