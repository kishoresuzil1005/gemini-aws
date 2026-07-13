"""
Region Manager — Production Implementation
Queries AWS, Azure, and GCP APIs for live region lists.
"""
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Known static fallbacks used when SDK calls are unavailable
_AWS_FALLBACK_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-west-2", "eu-central-1",
    "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
]

_GCP_FALLBACK_REGIONS = [
    "us-central1", "us-east1", "us-west1",
    "europe-west1", "europe-west2",
    "asia-east1", "asia-southeast1",
]

_AZURE_FALLBACK_REGIONS = [
    "eastus", "eastus2", "westus", "westus2",
    "northeurope", "westeurope",
    "southeastasia", "eastasia",
]


class RegionManager:
    """Centralizes region handling across all cloud providers."""

    def __init__(self):
        self._cache: Dict[str, List[str]] = {}
        self._defaults = {
            "aws": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            "azure": os.environ.get("AZURE_DEFAULT_REGION", "eastus"),
            "gcp": os.environ.get("GCP_DEFAULT_REGION", "us-central1"),
            "kubernetes": "global",
        }

    def get_default_region(self, provider: str) -> str:
        return self._defaults.get(provider.lower(), "global")

    # ─── AWS ────────────────────────────────────────────────────────────────────

    def get_aws_regions(self, refresh: bool = False) -> List[str]:
        """Returns all enabled AWS regions by calling EC2 DescribeRegions."""
        if "aws" in self._cache and not refresh:
            return self._cache["aws"]

        try:
            import boto3
            ec2 = boto3.client("ec2", region_name=self._defaults["aws"])
            resp = ec2.describe_regions(Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}])
            regions = [r["RegionName"] for r in resp.get("Regions", [])]
            self._cache["aws"] = regions
            logger.info(f"Discovered {len(regions)} AWS regions.")
            return regions
        except Exception as e:
            logger.warning(f"Could not fetch AWS regions ({e}), using fallback list.")
            return _AWS_FALLBACK_REGIONS

    def get_active_regions(self, provider: str) -> List[str]:
        """Returns active regions for the given provider."""
        p = provider.lower()
        if p == "aws":
            return self.get_aws_regions()
        elif p == "azure":
            return self._get_azure_regions()
        elif p == "gcp":
            return self._get_gcp_regions()
        return [self.get_default_region(provider)]

    def _get_azure_regions(self) -> List[str]:
        if "azure" in self._cache:
            return self._cache["azure"]
        try:
            from azure.identity import DefaultAzureCredential
            from azure.mgmt.resource import SubscriptionClient
            credential = DefaultAzureCredential()
            sub_client = SubscriptionClient(credential)
            sub_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
            from azure.mgmt.resource import ResourceManagementClient
            res_client = ResourceManagementClient(credential, sub_id)
            locations = [loc.name for loc in res_client.providers.get("Microsoft.Compute").resource_types[0].locations]
            self._cache["azure"] = locations or _AZURE_FALLBACK_REGIONS
            return self._cache["azure"]
        except Exception as e:
            logger.warning(f"Azure region discovery failed ({e}), using fallback.")
            return _AZURE_FALLBACK_REGIONS

    def _get_gcp_regions(self) -> List[str]:
        if "gcp" in self._cache:
            return self._cache["gcp"]
        try:
            from google.cloud import compute_v1
            project = os.environ.get("GCP_PROJECT_ID", "")
            client = compute_v1.RegionsClient()
            regions = [r.name for r in client.list(project=project)]
            self._cache["gcp"] = regions
            return regions
        except Exception as e:
            logger.warning(f"GCP region discovery failed ({e}), using fallback.")
            return _GCP_FALLBACK_REGIONS

    def get_failover_region(self, provider: str, failed_region: str) -> Optional[str]:
        """Returns an alternate region when the specified one fails."""
        regions = self.get_active_regions(provider)
        fallbacks = [r for r in regions if r != failed_region]
        return fallbacks[0] if fallbacks else None


region_manager = RegionManager()