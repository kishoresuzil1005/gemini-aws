import boto3

class ALBDiscovery:
    @staticmethod
    def discover(region):
        try:
            client = boto3.client("elbv2", region_name=region)
            response = client.describe_load_balancers()
            lbs = []
            for lb in response.get("LoadBalancers", []):
                lbs.append({
                    "resource_id": lb["LoadBalancerName"],
                    "resource_type": "ALB",
                    "region": region,
                    "dns_name": lb.get("DNSName"),
                    "scheme": lb.get("Scheme"),
                    "state": lb.get("State", {}).get("Code")
                })
            return lbs
        except Exception:
            return []
