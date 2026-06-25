import boto3

class RegionService:
    @staticmethod
    def get_regions():
        try:
            # Try to fetch actual AWS regions using boto3
            ec2 = boto3.client(
                "ec2",
                region_name="us-east-1"
            )
            response = ec2.describe_regions(
                AllRegions=False
            )
            regions = []
            for region in response["Regions"]:
                regions.append({
                    "name": region["RegionName"],
                    "endpoint": region["Endpoint"]
                })
            return sorted(
                regions,
                key=lambda x: x["name"]
            )
        except Exception as e:
            # Robust fallback to standard AWS regions when boto3 is not authenticated/offline
            fallback_regions = [
                {"name": "ap-south-1", "endpoint": "ec2.ap-south-1.amazonaws.com"},
                {"name": "ap-southeast-1", "endpoint": "ec2.ap-southeast-1.amazonaws.com"},
                {"name": "eu-central-1", "endpoint": "ec2.eu-central-1.amazonaws.com"},
                {"name": "us-east-1", "endpoint": "ec2.us-east-1.amazonaws.com"},
                {"name": "us-east-2", "endpoint": "ec2.us-east-2.amazonaws.com"},
                {"name": "us-west-1", "endpoint": "ec2.us-west-1.amazonaws.com"},
                {"name": "us-west-2", "endpoint": "ec2.us-west-2.amazonaws.com"}
            ]
            return sorted(
                fallback_regions,
                key=lambda x: x["name"]
            )
