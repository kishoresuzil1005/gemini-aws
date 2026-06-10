import boto3

class EBSDiscovery:
    @staticmethod
    def discover(region):
        try:
            client = boto3.client("ec2", region_name=region)
            response = client.describe_volumes()
            volumes = []
            for vol in response.get("Volumes", []):
                volumes.append({
                    "resource_id": vol["VolumeId"],
                    "resource_type": "EBS",
                    "region": region,
                    "size_gb": vol.get("Size"),
                    "state": vol.get("State"),
                    "attachments": len(vol.get("Attachments", []))
                })
            return volumes
        except Exception:
            return []
