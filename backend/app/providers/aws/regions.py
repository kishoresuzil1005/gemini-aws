import boto3

class RegionsDiscovery:
    @staticmethod
    def discover_enabled_regions():
        """
        Retrieves active or enabled AWS regions.
        """
        try:
            client = boto3.client("ec2")
            response = client.describe_regions()
            return [r["RegionName"] for r in response.get("Regions", [])]
        except Exception:
            # High-fidelity fallback list of default active regional endpoints
            return [
                "ap-south-1", "us-east-1", "ap-southeast-1", "eu-central-1",
                "ap-northeast-1", "ap-northeast-2", "ap-northeast-3", "ca-central-1",
                "eu-west-1", "eu-west-2", "eu-west-3", "us-west-1", "us-west-2",
                "us-east-2", "sa-east-1", "ap-southeast-2", "eu-north-1", "me-south-1"
            ]
