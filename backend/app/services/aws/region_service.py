import boto3
import logging

logger = logging.getLogger("RegionService")

class AWSRegionService:
    @staticmethod
    def get_regions(credentials=None):
        fallback_regions = [
            {"name": "ap-south-1", "endpoint": "ec2.ap-south-1.amazonaws.com"},
            {"name": "ap-southeast-1", "endpoint": "ec2.ap-southeast-1.amazonaws.com"},
            {"name": "eu-central-1", "endpoint": "ec2.eu-central-1.amazonaws.com"},
            {"name": "us-east-1", "endpoint": "ec2.us-east-1.amazonaws.com"},
            {"name": "us-east-2", "endpoint": "ec2.us-east-2.amazonaws.com"},
            {"name": "us-west-1", "endpoint": "ec2.us-west-1.amazonaws.com"},
            {"name": "us-west-2", "endpoint": "ec2.us-west-2.amazonaws.com"}
        ]
        
        if credentials and not credentials.get("success", False):
            return sorted(fallback_regions, key=lambda x: x["name"])

        try:
            kwargs = {"region_name": "us-east-1"}
            if credentials:
                kwargs["aws_access_key_id"] = credentials["access_key"]
                kwargs["aws_secret_access_key"] = credentials["secret_key"]
                kwargs["aws_session_token"] = credentials["session_token"]

            ec2 = boto3.client("ec2", **kwargs)
            response = ec2.describe_regions(AllRegions=False)
            return sorted([
                {
                    "name": region["RegionName"],
                    "endpoint": region["Endpoint"]
                }
                for region in response["Regions"]
            ], key=lambda x: x["name"])
        except Exception as e:
            logger.warning(f"Failed to fetch regions natively: {e}. Returning robust region list fallback.")
            return sorted(fallback_regions, key=lambda x: x["name"])

    @staticmethod
    def get_all_regions():
        regions = AWSAWSRegionService.get_regions()
        return [r["name"] for r in regions]