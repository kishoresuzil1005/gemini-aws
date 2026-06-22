import boto3
from app.services.region_service import RegionService

class AWSRegionService:
    @staticmethod
    def get_all_regions():
        # Delegate to RegionService to get region list and extract names
        regions = RegionService.get_regions()
        return [r["name"] for r in regions]
