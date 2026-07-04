import logging
from typing import Tuple, List, Dict, Any

from app.services.discovery.scanner import AWSDiscoveryScanner
from app.services.discovery.normalizer import ResourceNormalizer
from app.config import is_aws_configured

logger = logging.getLogger("AWS_Legacy_Scanner")

def scan_aws_resources() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Legacy wrapper for backwards compatibility with the Incident Engine and older routes.
    Now delegates completely to AWSDiscoveryScanner (Phase 4).
    """
    if not is_aws_configured():
        raise Exception("AWS credentials not configured")

    logger.info("Executing Phase 4 Unified Discovery via legacy wrapper...")
    
    # Delegate to the single source of truth
    scan_result = AWSDiscoveryScanner.scan_all()
    
    # Normalize resources for backward compatibility mapping
    normalized_resources = ResourceNormalizer.normalize(scan_result.resources)
    
    # Phase 4: Incidents are now evaluated offline via incident_engine.py
    # We return an empty incidents list to preserve legacy API signature
    return normalized_resources, []
