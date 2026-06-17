import boto3
import logging

logger = logging.getLogger(__name__)


def get_all_regions():
    """
    Returns all enabled AWS regions
    """

    try:

        client = boto3.client(
            "ec2",
            region_name="us-east-1"
        )

        response = client.describe_regions(
            AllRegions=False
        )

        regions = [
            region["RegionName"]
            for region in response["Regions"]
        ]

        logger.info(
            f"Found {len(regions)} AWS regions"
        )

        return regions

    except Exception as e:

        logger.error(
            f"Failed to load regions: {e}"
        )

        return [
            "ap-south-1", "us-east-1", "ap-southeast-1", "eu-central-1",
            "ap-northeast-1", "ap-northeast-2", "ap-northeast-3", "ca-central-1",
            "eu-west-1", "eu-west-2", "eu-west-3", "us-west-1", "us-west-2",
            "us-east-2", "sa-east-1", "ap-southeast-2", "eu-north-1", "me-south-1"
        ]
