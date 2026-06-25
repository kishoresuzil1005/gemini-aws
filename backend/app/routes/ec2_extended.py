from fastapi import APIRouter, HTTPException
import logging

from app.services.aws.ec2_extended_service import (
    EC2ExtendedService
)
from app.services.cache.ec2_cache import EC2Cache

logger = logging.getLogger(__name__)
router = APIRouter(tags=["EC2-Extended"])


@router.get("/api/ec2/extended")
def ec2_extended(
    region: str = "ap-south-1"
):
    cached = EC2Cache.get_extended(region)
    if cached:
        return cached

    service = EC2ExtendedService(region)
    data = service.get_extended_summary()
    EC2Cache.set_extended(region, data)
    return data


@router.get("/api/ec2/launch_templates")
def get_launch_templates(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_launch_templates_details()
    except Exception as e:
        logger.exception("Launch Templates route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/spot_requests")
def get_spot_requests(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_spot_requests_details()
    except Exception as e:
        logger.exception("Spot Requests route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/savings_plans")
def get_savings_plans(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_savings_plans_details()
    except Exception as e:
        logger.exception("Savings Plans route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/reserved_instances")
def get_reserved_instances(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_reserved_instances_details()
    except Exception as e:
        logger.exception("Reserved Instances route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/dedicated_hosts")
def get_dedicated_hosts(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_dedicated_hosts_details()
    except Exception as e:
        logger.exception("Dedicated Hosts route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/dedicated_hosts/reservations")
def get_dedicated_host_reservations(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_dedicated_host_reservations()
    except Exception as e:
        logger.exception("Host Reservations route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/amis")
def get_amis(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_amis_details()
    except Exception as e:
        logger.exception("AMIs route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/ami_catalog")
def get_ami_catalog(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_ami_catalog_details()
    except Exception as e:
        logger.exception("AMI Catalog route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/volumes")
def get_volumes(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_volumes_details()
    except Exception as e:
        logger.exception("Volumes route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/snapshots")
def get_snapshots(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_snapshots_details()
    except Exception as e:
        logger.exception("Snapshots route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/security_groups")
def get_security_groups(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_security_groups_details()
    except Exception as e:
        logger.exception("Security Groups route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/elastic_ips")
def get_elastic_ips(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_elastic_ips_details()
    except Exception as e:
        logger.exception("Elastic IPs route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/placement_groups")
def get_placement_groups(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_placement_groups_details()
    except Exception as e:
        logger.exception("Placement Groups route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/key_pairs")
def get_key_pairs(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_key_pairs_details()
    except Exception as e:
        logger.exception("Key Pairs route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/network_interfaces")
def get_network_interfaces(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_network_interfaces_details()
    except Exception as e:
        logger.exception("Network Interfaces route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/load_balancers")
def get_load_balancers(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_load_balancers_details()
    except Exception as e:
        logger.exception("Load Balancers route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/target_groups")
def get_target_groups(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_target_groups_details()
    except Exception as e:
        logger.exception("Target Groups route error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/ec2/trust_stores")
def get_trust_stores(region: str = "ap-south-1"):
    try:
        service = EC2ExtendedService(region)
        return service.get_trust_stores_details()
    except Exception as e:
        logger.exception("Trust Stores route error")
        raise HTTPException(status_code=500, detail=str(e))
