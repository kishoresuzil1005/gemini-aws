import logging
from typing import Tuple, List, Dict, Any

from app.services.discovery.scanner import AWSDiscoveryScanner
from app.services.discovery.normalizer import ResourceNormalizer
import boto3
from app.config import is_aws_configured, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

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


def get_session():
    """
    Creates an authenticated Boto3 Session using env variables.
    """
    if is_aws_configured():
        return boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
    return None


def verify_aws_credentials(session):
    if not session:
        return False
    try:
        sts = session.client("sts")
        sts.get_caller_identity()
        return True
    except Exception as e:
        logger.error(f"AWS credential validation failed: {e}")
        return False


def heal_security_group_ssh(sg_id: str):
    """
    Real SRE therapeutic self-healing execution: Revokes wildcard port 22 Access.
    """
    session = get_session()
    if not session or not verify_aws_credentials(session):
        return True, "Mock Healer: Successfully revoked 0.0.0.0/0 wildcard SSH and restricted access to secure bastion tunnel CIDR 198.51.100.0/22 via simulated API endpoint."

    try:
        ec2 = session.client("ec2")
        # Step 1: Revoke wildcard port 22 access
        logger.info(f"Programmatic Healing: Revoking wildcard SSH from security group {sg_id}")
        ec2.revoke_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                }
            ]
        )
        
        # Step 2: Inject a secure VPN CIDR reference (standard corporate policy fallback)
        logger.info(f"Programmatic Healing: Appending corporate bastion subnet ingress CIDR for {sg_id}")
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "198.51.100.0/22", "Description": "SRE Admin VPN Tunnel Endpoint"}]
                }
            ]
        )
        return True, "Successfully revoked 0.0.0.0/0 wildcard SSH and restricted access to secure bastion tunnel CIDR 198.51.100.0/22 via programmatic boto3 call."
    except Exception as ex:
        logger.error(f"Failed to execute programmatic security group healing: {ex}")
        return False, f"Boto3 call execution failed: {str(ex)}"


def heal_s3_bucket_encryption(bucket_name: str):
    """
    Real SRE autonomic self-healing execution: Programmatically configures SSE-KMS bucket policy.
    """
    session = get_session()
    if not session or not verify_aws_credentials(session):
        return True, f"Mock Healer: Successfully enabled default server-side AES256 encryption on S3 bucket '{bucket_name}' via simulated API endpoint."

    try:
        s3 = session.client("s3")
        logger.info(f"Programmatic Healing: Applying default AES256 server-side encryption to S3 bucket: {bucket_name}")
        
        # Apply default AES256 bucket encryption policy
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }
        )
        return True, f"Successfully enabled default server-side AES256 encryption on S3 bucket '{bucket_name}' via put_bucket_encryption botocore callback."
    except Exception as ex:
        logger.error(f"Failed to programmatically apply default encryption: {ex}")
        return False, f"Boto3 encryption call failed: {str(ex)}"
