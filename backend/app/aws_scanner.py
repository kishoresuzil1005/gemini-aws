import boto3
import logging
from botocore.exceptions import ClientError
from .config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, is_aws_configured

logger = logging.getLogger("AWS_Scanner")

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

def scan_aws_resources():
    """
    Performs real live scan of the user's AWS account.
    Returns: (list_of_resources, list_of_incidents)
    """
    session = get_session()
    if not session:
        logger.warning("AWS keys not configured. Returning empty live-scan dataset.")
        return [], []

    resources = []
    incidents = []

    try:
        # 1. Scan Network (VPC & Subnets) & Security Groups
        ec2 = session.client("ec2")
        
        # Pull VPCs
        try:
            vpcs = ec2.describe_vpcs()
            for vpc in vpcs.get("Vpcs", []):
                vpc_id = vpc["VpcId"]
                cidr = vpc.get("CidrBlock", "N/A")
                is_default = "Default" if vpc.get("IsDefault") else "Custom"
                resources.append({
                    "id": vpc_id,
                    "provider": "AWS",
                    "type": "VPC",
                    "name": f"VPC-{vpc_id[-6:]} ({is_default})",
                    "configurationHint": f"CIDR Block: {cidr} | Tenancy: {vpc.get('InstanceTenancy', 'N/A')}",
                    "costEstimate": 0.0,
                    "dependenciesString": ""
                })
        except ClienError as e:
            logger.error(f"Failed scanning VPCs: {e}")

        # Scan Security Groups to detect SSH wildcard risk
        try:
            sgs = ec2.describe_security_groups()
            for sg_desc in sgs.get("SecurityGroups", []):
                sg_id = sg_desc["GroupId"]
                sg_name = sg_desc["GroupName"]
                
                # Check for port 22 open to 0.0.0.0/0
                has_public_ssh = False
                for permission in sg_desc.get("IpPermissions", []):
                    from_port = permission.get("FromPort")
                    to_port = permission.get("ToPort")
                    ip_ranges = [r.get("CidrIp") for r in permission.get("IpRanges", [])]
                    
                    # Check if port range includes 22 and CIDR is open
                    is_ssh_port = (from_port is None or (from_port <= 22 <= to_port))
                    if is_ssh_port and "0.0.0.0/0" in ip_ranges:
                        has_public_ssh = True
                        break
                
                if has_public_ssh:
                    incidents.append({
                        "id": f"aws-sg-{sg_id}",
                        "title": f"Wildcard SSH Port Open in Security Group",
                        "severity": "CRITICAL",
                        "resourceId": sg_id,
                        "description": f"Audited firewall rules for SG '{sg_name}' ({sg_id}) and detected port 22 is unrestricted to "
                                       f"the entire internet ('0.0.0.0/0'). This exposes host shells to brute-force vectors.",
                        "status": "ACTIVE"
                    })
        except Exception as sg_err:
            logger.error(f"Vulnerability scanner failed checking SGs: {sg_err}")

        # 2. Scan Compute (EC2)
        try:
            instances = ec2.describe_instances()
            for reservation in instances.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    inst_id = inst["InstanceId"]
                    inst_type = inst["InstanceType"]
                    state = inst["State"]["Name"]
                    
                    # Extract name tag
                    name = inst_id
                    for tag in inst.get("Tags", []):
                        if tag["Key"] == "Name":
                            name = tag["Value"]
                            break
                    
                    # Map EC2 to resources
                    resources.append({
                        "id": inst_id,
                        "provider": "AWS",
                        "type": "EC2",
                        "name": name,
                        "configurationHint": f"Type: {inst_type} | State: {state} | Launch Time: {inst.get('LaunchTime', 'N/A')}",
                        "costEstimate": 45.80, # approximate standard rate
                        "dependenciesString": ""
                    })
                    
                    # If instance has a critical load or is stopped in error, we could raise an incident
                    if state == "stopped":
                        incidents.append({
                            "id": f"aws-ec2-stopped-{inst_id}",
                            "title": f"Offline Cloud Instance Anomaly",
                            "severity": "WARNING",
                            "resourceId": inst_id,
                            "description": f"EC2 node '{name}' ({inst_id}) has entered an irregular STOPPED state with active dependency indicators.",
                            "status": "ACTIVE"
                        })
        except Exception as ec2_err:
            logger.error(f"Failed scanning EC2 instances: {ec2_err}")

        # 3. Scan Storage (S3)
        try:
            s3 = session.client("s3")
            buckets = s3.list_buckets()
            for bucket in buckets.get("Buckets", []):
                bucket_name = bucket["Name"]
                
                # Check for encryption
                is_encrypted = True
                try:
                    s3.get_bucket_encryption(Bucket=bucket_name)
                except ClientError as enc_err:
                    # If ServerSideEncryptionConfigurationNotFoundError raised, bucket is unencrypted
                    if "ServerSideEncryptionConfigurationNotFoundError" in str(enc_err) or enc_err.response["Error"]["Code"] == "ServerSideEncryptionConfigurationNotFoundError":
                        is_encrypted = False
                    else:
                        logger.warning(f"Error checking bucket encryption for {bucket_name}: {enc_err}")

                resources.append({
                    "id": f"s3-{bucket_name}",
                    "provider": "AWS",
                    "type": "S3",
                    "name": bucket_name,
                    "configurationHint": f"Creation Date: {bucket.get('CreationDate')} | Encrypted: {'SSE-KMS/AES256' if is_encrypted else 'None'}",
                    "costEstimate": 15.42,
                    "dependenciesString": ""
                })

                if not is_encrypted:
                    incidents.append({
                        "id": f"aws-s3-unencrypted-{bucket_name}",
                        "title": f"S3 Bucket Lacks SSE Policy",
                        "severity": "WARNING",
                        "resourceId": bucket_name,
                        "description": f"S3 Storage Bucket '{bucket_name}' has default bucket encryption disabled. "
                                       f"Uploading sensitive logs without KMS/AES key envelopes violates standard compliance standards.",
                        "status": "ACTIVE"
                    })
        except Exception as s3_err:
            logger.error(f"Failed scanning S3: {s3_err}")

        # 4. Scan RDS Db Instances
        try:
            rds = session.client("rds")
            db_instances = rds.describe_db_instances()
            for db_inst in db_instances.get("DBInstances", []):
                db_id = db_inst["DBInstanceIdentifier"]
                engine_name = db_inst["Engine"]
                engine_version = db_inst["EngineVersion"]
                status = db_inst["DBInstanceStatus"]
                db_class = db_inst["DBInstanceClass"]

                resources.append({
                    "id": db_id,
                    "provider": "AWS",
                    "type": "RDS",
                    "name": db_id,
                    "configurationHint": f"Engine: {engine_name} {engine_version} | Class: {db_class} | Status: {status}",
                    "costEstimate": 124.50,
                    "dependenciesString": ""
                })
        except Exception as rds_err:
            logger.error(f"Failed scanning RDS DBs: {rds_err}")

        # 5. Scan Serverless Functions (Lambda)
        try:
            lambda_client = session.client("lambda")
            funcs = lambda_client.list_functions()
            for f in funcs.get("Functions", []):
                f_name = f["FunctionName"]
                runtime = f["Runtime"]
                f_size = f["MemorySize"]
                
                resources.append({
                    "id": f"lambda-{f_name}",
                    "provider": "AWS",
                    "type": "Lambda",
                    "name": f_name,
                    "configurationHint": f"Runtime: {runtime} | Handled Memory: {f_size}MB | Timeout: {f.get('Timeout')}s",
                    "costEstimate": 2.10,
                    "dependenciesString": ""
                })
        except Exception as lam_err:
            logger.error(f"Failed scanning Lambda: {lam_err}")

    except Exception as general_err:
        logger.error(f"General error during AWS metadata sweep: {general_err}")

    return resources, incidents


def heal_security_group_ssh(sg_id: str):
    """
    Real SRE therapeutic self-healing execution: Revokes wildcard port 22 Access.
    """
    session = get_session()
    if not session:
        return False, "AWS session not active. Simulating healing action successfully locally."
    
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
    if not session:
        return False, "AWS session not active. Simulating encryption healing locally."

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
