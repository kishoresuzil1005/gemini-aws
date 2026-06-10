import boto3

class EKSDiscovery:
    @staticmethod
    def discover(region):
        try:
            client = boto3.client("eks", region_name=region)
            response = client.list_clusters()
            clusters = []
            for name in response.get("clusters", []):
                clusters.append({
                    "resource_id": name,
                    "resource_type": "EKS",
                    "region": region
                })
            return clusters
        except Exception:
            return []
