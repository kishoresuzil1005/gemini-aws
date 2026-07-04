import boto3
import json
import logging
import time
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import PricingCacheDB

logger = logging.getLogger("PricingService")

# High-fidelity on-demand SRE industry default hourly rates (USD)
FALLBACK_PRICES = {
    "EC2": {
        "t3.nano": 0.0052,
        "t3.micro": 0.0104,
        "t3.small": 0.0208,
        "t3.medium": 0.0416,
        "t3.large": 0.0832,
        "t3.xlarge": 0.1664,
        "t2.micro": 0.0116,
        "t2.small": 0.023,
        "t2.medium": 0.0464,
        "m5.large": 0.096,
        "m5.xlarge": 0.192,
        "c5.large": 0.085,
        "c5.xlarge": 0.170,
        "default": 0.0416  # t3.medium fallback
    },
    "RDS": {
        "db.t3.micro": 0.017,
        "db.t3.small": 0.034,
        "db.t3.medium": 0.068,
        "db.t3.large": 0.136,
        "db.m5.large": 0.175,
        "db.m5.xlarge": 0.350,
        "default": 0.068
    },
    "EBS": {
        "gp2": 0.10,     # per GB/Month
        "gp3": 0.08,     # per GB/Month
        "io1": 0.125,    # per GB/Month
        "st1": 0.045,    # per GB/Month
        "default": 0.08
    },
    "S3": {
        "Standard": 0.023,    # per GB/Month
        "Infrequent": 0.0125, # per GB/Month
        "Glacier": 0.004,     # per GB/Month
        "default": 0.023
    },
    "Lambda": {
        "request_rate": 0.0000002,     # 0.20 per million calls
        "compute_gb_sec": 0.0000166667 # x86 architecture standard rate
    }
}

class PricingService:
    def __init__(self, db: Session = None):
        self.db = db
        try:
            self.pricing_client = boto3.client("pricing", region_name="us-east-1")
        except Exception:
            self.pricing_client = None

    def get_hourly_price(self, service: str, resource_type: str, region: str = "us-east-1") -> float:
        """
        Attempts to acquire the optimal, real-time pricing coefficient.
        Consults local cache, seeks AWS product code via Boto3, or serves fallback specifications.
        """
        # 1. Look in PostgreSQL local cache first
        if self.db:
            try:
                cached = self.db.query(PricingCacheDB).filter(
                    PricingCacheDB.service == service,
                    PricingCacheDB.resource_type == resource_type,
                    PricingCacheDB.region == region
                ).first()
                if cached:
                    return cached.price_per_hour
            except Exception as ce:
                logger.warning(f"Error querying pricing cache from DB: {ce}")

        # 2. Inquire live AWS Pricing API (Phase 4 capability)
        if self.pricing_client:
            try:
                if service == "EC2":
                    aws_service_code = "AmazonEC2"
                    filters = [
                        {"Type": "TERM_MATCH", "Field": "instanceType", "Value": resource_type},
                        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                        {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                        {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                        {"Type": "TERM_MATCH", "Field": "location", "Value": self._get_location_name(region)}
                    ]
                    response = self.pricing_client.get_products(
                        ServiceCode=aws_service_code,
                        Filters=filters,
                        MaxResults=1
                    )
                    price = self._extract_price_from_response(response)
                    if price > 0:
                        self._update_local_cache(service, resource_type, price, region)
                        return price

                elif service == "RDS":
                    aws_service_code = "AmazonRDS"
                    filters = [
                        {"Type": "TERM_MATCH", "Field": "instanceType", "Value": resource_type},
                        {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": "PostgreSQL"},
                        {"Type": "TERM_MATCH", "Field": "location", "Value": self._get_location_name(region)}
                    ]
                    response = self.pricing_client.get_products(
                        ServiceCode=aws_service_code,
                        Filters=filters,
                        MaxResults=1
                    )
                    price = self._extract_price_from_response(response)
                    if price > 0:
                        self._update_local_cache(service, resource_type, price, region)
                        return price
            except Exception as api_err:
                logger.info(f"Using high-fidelity local models; AWS Pricing API unavailable: {api_err}")

        # 3. Use high-fidelity SRE fallbacks if cache or live fetch misses
        service_fallback = FALLBACK_PRICES.get(service, {})
        hourly_coefficient = service_fallback.get(resource_type, service_fallback.get("default", 0.0))
        
        # Hydrate local cache with this standard seed rate
        if self.db and hourly_coefficient > 0:
            try:
                self._update_local_cache(service, resource_type, hourly_coefficient, region)
            except Exception as db_exc:
                logger.warning(f"Failed to hydrate local cache: {db_exc}")

        return hourly_coefficient

    def _update_local_cache(self, service: str, resource_type: str, price: float, region: str):
        if not self.db:
            return
        
        # Check if already present to prevent duplicating rows
        existing = self.db.query(PricingCacheDB).filter(
            PricingCacheDB.service == service,
            PricingCacheDB.resource_type == resource_type,
            PricingCacheDB.region == region
        ).first()

        if existing:
            existing.price_per_hour = price
            existing.updated_at = datetime.utcnow()
        else:
            new_entry = PricingCacheDB(
                service=service,
                sku=f"SKU-{service}-{resource_type}",
                resource_type=resource_type,
                price_per_hour=price,
                region=region,
                updated_at=datetime.utcnow()
            )
            self.db.add(new_entry)
        self.db.commit()

    def _extract_price_from_response(self, response) -> float:
        try:
            price_list = response.get("PriceList", [])
            if not price_list:
                return 0.0
            product_data = json.loads(price_list[0])
            terms = product_data.get("terms", {}).get("OnDemand", {})
            for term_key in terms.keys():
                price_dimensions = terms[term_key].get("priceDimensions", {})
                for dim_key in price_dimensions.keys():
                    price_per_unit = price_dimensions[dim_key].get("pricePerUnit", {})
                    usd_price = price_per_unit.get("USD")
                    if usd_price is not None:
                        return float(usd_price)
        except Exception:
            pass
        return 0.0

    def _get_location_name(self, region: str) -> str:
        region_map = {
            "us-east-1": "US East (N. Virginia)",
            "us-west-2": "US West (Oregon)",
            "eu-central-1": "Europe (Frankfurt)",
            "ap-south-1": "Asia Pacific (Mumbai)"
        }
        return region_map.get(region, "US East (N. Virginia)")
