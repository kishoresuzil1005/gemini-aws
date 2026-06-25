import boto3
import logging

logger = logging.getLogger("RegionService")

class RegionService:
    @staticmethod
    def get_regions(credentials):
        fallback_regions = [
            {"name": "ap-south-1", "endpoint": "ec2.ap-south-1.amazonaws.com"},
            {"name": "us-east-1", "endpoint": "ec2.us-east-1.amazonaws.com"},
            {"name": "ap-southeast-1", "endpoint": "ec2.ap-southeast-1.amazonaws.com"},
            {"name": "eu-central-1", "endpoint": "ec2.eu-central-1.amazonaws.com"},
            {"name": "us-east-2", "endpoint": "ec2.us-east-2.amazonaws.com"},
            {"name": "us-west-1", "endpoint": "ec2.us-west-1.amazonaws.com"},
            {"name": "us-west-2", "endpoint": "ec2.us-west-2.amazonaws.com"}
        ]
        
        # If the AWS assumption was mock/failed, immediately return the standard fallback list
        if not credentials.get("success", False):
            return sorted(fallback_regions, key=lambda x: x["name"])

        try:
            ec2 = boto3.client(
                "ec2",
                region_name="us-east-1",
                aws_access_key_id=credentials["access_key"],
                aws_secret_access_key=credentials["secret_key"],
                aws_session_token=credentials["session_token"]
            )
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
