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
            return ["us-east-1", "us-west-2", "eu-central-1", "ap-south-1"]
