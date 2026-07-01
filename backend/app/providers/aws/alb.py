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
                    "resource_id": lb["LoadBalancerArn"],
                    "resource_type": "ALB",
                    "region": region,
                    "name": lb["LoadBalancerName"],
                    "dns_name": lb.get("DNSName"),
                    "scheme": lb.get("Scheme"),
                    "state": lb.get("State", {}).get("Code")
                })
                
            tg_response = client.describe_target_groups()
            for tg in tg_response.get("TargetGroups", []):
                lbs.append({
                    "resource_id": tg["TargetGroupArn"],
                    "resource_type": "TargetGroup",
                    "region": region,
                    "name": tg["TargetGroupName"]
                })
                
            return lbs
        except Exception:
            return []
