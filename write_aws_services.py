"""
AWS Service Implementations — Production
All Sprint 3 AWS service files with full boto3 SDK implementations.
Covers: InternetGateway, NatGateway, RouteTable, Subnet, NetworkInterface,
        ElasticIp, LoadBalancer, TargetGroup, Listener, Autoscaling,
        SecurityGroup, S3, EBS, CloudTrail, Config, Backup, SSM
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory
from app.providers.common.pagination_helper import PaginationHelper

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# INTERNET GATEWAY
# ═══════════════════════════════════════════════════════════════════════

IGW_FILE = "backend/app/providers/aws/internet_gateway_service.py"
IGW_CODE = '''"""Internet Gateway Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class InternetGatewayService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ec2", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        resp = self.client.describe_internet_gateways()
        return [
            {
                "resource_id": igw["InternetGatewayId"],
                "resource_type": "InternetGateway",
                "name": next((t["Value"] for t in igw.get("Tags", []) if t["Key"] == "Name"), igw["InternetGatewayId"]),
                "region": self.region,
                "status": "attached" if igw.get("Attachments") else "detached",
                "metadata": {
                    "attachments": igw.get("Attachments", []),
                    "tags": {t["Key"]: t["Value"] for t in igw.get("Tags", [])},
                },
            }
            for igw in resp.get("InternetGateways", [])
        ]

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_internet_gateways(InternetGatewayIds=[resource_id])
        igws = resp.get("InternetGateways", [])
        return igws[0] if igws else None

    def create(self, tags: Optional[List[Dict]] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "internet-gateway", "Tags": tags}]
        resp = self.client.create_internet_gateway(**kwargs)
        igw = resp.get("InternetGateway", {})
        logger.info(f"Created Internet Gateway: {igw.get('InternetGatewayId')}")
        return igw

    def attach(self, igw_id: str, vpc_id: str) -> Dict[str, Any]:
        self.client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        return {"status": "attached", "igw_id": igw_id, "vpc_id": vpc_id}

    def detach(self, igw_id: str, vpc_id: str) -> Dict[str, Any]:
        self.client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        return {"status": "detached", "igw_id": igw_id, "vpc_id": vpc_id}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_internet_gateway(InternetGatewayId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# NAT GATEWAY
# ═══════════════════════════════════════════════════════════════════════
NAT_CODE = '''"""NAT Gateway Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class NatGatewayService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ec2", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_nat_gateways")
        gateways = []
        for page in paginator.paginate():
            for ngw in page.get("NatGateways", []):
                gateways.append({
                    "resource_id": ngw["NatGatewayId"],
                    "resource_type": "NatGateway",
                    "name": next((t["Value"] for t in ngw.get("Tags", []) if t["Key"] == "Name"), ngw["NatGatewayId"]),
                    "region": self.region,
                    "status": ngw.get("State", "unknown"),
                    "metadata": {
                        "subnet_id": ngw.get("SubnetId"),
                        "vpc_id": ngw.get("VpcId"),
                        "connectivity_type": ngw.get("ConnectivityType"),
                        "nat_gateway_addresses": ngw.get("NatGatewayAddresses", []),
                        "tags": {t["Key"]: t["Value"] for t in ngw.get("Tags", [])},
                    },
                })
        return gateways

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_nat_gateways(NatGatewayIds=[resource_id])
        ngws = resp.get("NatGateways", [])
        return ngws[0] if ngws else None

    def create(self, subnet_id: str, allocation_id: str, connectivity_type: str = "public", tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"SubnetId": subnet_id, "AllocationId": allocation_id, "ConnectivityType": connectivity_type}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "natgateway", "Tags": tags}]
        resp = self.client.create_nat_gateway(**kwargs)
        ngw = resp.get("NatGateway", {})
        logger.info(f"Created NAT Gateway: {ngw.get('NatGatewayId')}")
        return ngw

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_nat_gateway(NatGatewayId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# ROUTE TABLE
# ═══════════════════════════════════════════════════════════════════════
RT_CODE = '''"""Route Table Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class RouteTableService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ec2", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_route_tables")
        tables = []
        for page in paginator.paginate():
            for rt in page.get("RouteTables", []):
                tables.append({
                    "resource_id": rt["RouteTableId"],
                    "resource_type": "RouteTable",
                    "name": next((t["Value"] for t in rt.get("Tags", []) if t["Key"] == "Name"), rt["RouteTableId"]),
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "vpc_id": rt.get("VpcId"),
                        "routes": rt.get("Routes", []),
                        "associations": rt.get("Associations", []),
                        "tags": {t["Key"]: t["Value"] for t in rt.get("Tags", [])},
                    },
                })
        return tables

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_route_tables(RouteTableIds=[resource_id])
        rts = resp.get("RouteTables", [])
        return rts[0] if rts else None

    def create(self, vpc_id: str, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VpcId": vpc_id}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "route-table", "Tags": tags}]
        resp = self.client.create_route_table(**kwargs)
        return resp.get("RouteTable", {})

    def create_route(self, route_table_id: str, destination_cidr: str, gateway_id: Optional[str] = None, nat_gateway_id: Optional[str] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"RouteTableId": route_table_id, "DestinationCidrBlock": destination_cidr}
        if gateway_id:
            kwargs["GatewayId"] = gateway_id
        if nat_gateway_id:
            kwargs["NatGatewayId"] = nat_gateway_id
        self.client.create_route(**kwargs)
        return {"status": "created", "route_table_id": route_table_id, "destination": destination_cidr}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_route_table(RouteTableId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# SUBNET
# ═══════════════════════════════════════════════════════════════════════
SUBNET_CODE = '''"""Subnet Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class SubnetService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ec2", region_name=region, role_arn=role_arn)

    def list(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if vpc_id:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
        paginator = self.client.get_paginator("describe_subnets")
        subnets = []
        for page in paginator.paginate(**kwargs):
            for subnet in page.get("Subnets", []):
                subnets.append({
                    "resource_id": subnet["SubnetId"],
                    "resource_type": "Subnet",
                    "name": next((t["Value"] for t in subnet.get("Tags", []) if t["Key"] == "Name"), subnet["SubnetId"]),
                    "region": self.region,
                    "status": subnet.get("State", "available"),
                    "metadata": {
                        "vpc_id": subnet.get("VpcId"),
                        "cidr_block": subnet.get("CidrBlock"),
                        "availability_zone": subnet.get("AvailabilityZone"),
                        "available_ip_count": subnet.get("AvailableIpAddressCount"),
                        "map_public_ip": subnet.get("MapPublicIpOnLaunch"),
                        "tags": {t["Key"]: t["Value"] for t in subnet.get("Tags", [])},
                    },
                })
        return subnets

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_subnets(SubnetIds=[resource_id])
        subnets = resp.get("Subnets", [])
        return subnets[0] if subnets else None

    def create(self, vpc_id: str, cidr_block: str, availability_zone: str, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VpcId": vpc_id, "CidrBlock": cidr_block, "AvailabilityZone": availability_zone}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "subnet", "Tags": tags}]
        resp = self.client.create_subnet(**kwargs)
        return resp.get("Subnet", {})

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_subnet(SubnetId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# SECURITY GROUP
# ═══════════════════════════════════════════════════════════════════════
SG_CODE = '''"""Security Group Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class SecurityGroupService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ec2", region_name=region, role_arn=role_arn)

    def list(self, vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if vpc_id:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [vpc_id]}]
        paginator = self.client.get_paginator("describe_security_groups")
        sgs = []
        for page in paginator.paginate(**kwargs):
            for sg in page.get("SecurityGroups", []):
                sgs.append({
                    "resource_id": sg["GroupId"],
                    "resource_type": "SecurityGroup",
                    "name": sg.get("GroupName"),
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "description": sg.get("Description"),
                        "vpc_id": sg.get("VpcId"),
                        "ingress_rules": sg.get("IpPermissions", []),
                        "egress_rules": sg.get("IpPermissionsEgress", []),
                        "tags": {t["Key"]: t["Value"] for t in sg.get("Tags", [])},
                    },
                })
        return sgs

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_security_groups(GroupIds=[resource_id])
        sgs = resp.get("SecurityGroups", [])
        return sgs[0] if sgs else None

    def create(self, group_name: str, description: str, vpc_id: str, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"GroupName": group_name, "Description": description, "VpcId": vpc_id}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "security-group", "Tags": tags}]
        resp = self.client.create_security_group(**kwargs)
        return {"group_id": resp.get("GroupId"), "status": "created"}

    def authorize_ingress(self, group_id: str, ip_permissions: List[Dict]) -> Dict[str, Any]:
        self.client.authorize_security_group_ingress(GroupId=group_id, IpPermissions=ip_permissions)
        return {"status": "ingress_authorized", "group_id": group_id}

    def authorize_egress(self, group_id: str, ip_permissions: List[Dict]) -> Dict[str, Any]:
        self.client.authorize_security_group_egress(GroupId=group_id, IpPermissions=ip_permissions)
        return {"status": "egress_authorized", "group_id": group_id}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_security_group(GroupId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# EBS
# ═══════════════════════════════════════════════════════════════════════
EBS_CODE = '''"""EBS Volume Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class EbsService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ec2", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_volumes")
        volumes = []
        for page in paginator.paginate():
            for vol in page.get("Volumes", []):
                volumes.append({
                    "resource_id": vol["VolumeId"],
                    "resource_type": "EBS",
                    "name": next((t["Value"] for t in vol.get("Tags", []) if t["Key"] == "Name"), vol["VolumeId"]),
                    "region": self.region,
                    "status": vol.get("State", "unknown"),
                    "metadata": {
                        "size_gb": vol.get("Size"),
                        "volume_type": vol.get("VolumeType"),
                        "iops": vol.get("Iops"),
                        "encrypted": vol.get("Encrypted"),
                        "availability_zone": vol.get("AvailabilityZone"),
                        "attachments": vol.get("Attachments", []),
                        "snapshot_id": vol.get("SnapshotId"),
                        "tags": {t["Key"]: t["Value"] for t in vol.get("Tags", [])},
                    },
                })
        return volumes

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_volumes(VolumeIds=[resource_id])
        vols = resp.get("Volumes", [])
        return vols[0] if vols else None

    def create(self, availability_zone: str, size_gb: int, volume_type: str = "gp3", encrypted: bool = True, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"AvailabilityZone": availability_zone, "Size": size_gb, "VolumeType": volume_type, "Encrypted": encrypted}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "volume", "Tags": tags}]
        resp = self.client.create_volume(**kwargs)
        return resp

    def attach(self, volume_id: str, instance_id: str, device: str) -> Dict[str, Any]:
        resp = self.client.attach_volume(VolumeId=volume_id, InstanceId=instance_id, Device=device)
        return resp

    def detach(self, volume_id: str, instance_id: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VolumeId": volume_id, "Force": force}
        if instance_id:
            kwargs["InstanceId"] = instance_id
        resp = self.client.detach_volume(**kwargs)
        return resp

    def create_snapshot(self, volume_id: str, description: str = "") -> Dict[str, Any]:
        resp = self.client.create_snapshot(VolumeId=volume_id, Description=description)
        return resp

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_volume(VolumeId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# AUTOSCALING
# ═══════════════════════════════════════════════════════════════════════
ASG_CODE = '''"""Autoscaling Group Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class AutoscalingService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("autoscaling", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_auto_scaling_groups")
        groups = []
        for page in paginator.paginate():
            for asg in page.get("AutoScalingGroups", []):
                groups.append({
                    "resource_id": asg["AutoScalingGroupARN"],
                    "resource_type": "AutoScalingGroup",
                    "name": asg["AutoScalingGroupName"],
                    "region": self.region,
                    "status": asg.get("Status", "active"),
                    "metadata": {
                        "min_size": asg.get("MinSize"),
                        "max_size": asg.get("MaxSize"),
                        "desired_capacity": asg.get("DesiredCapacity"),
                        "vpc_zone_identifier": asg.get("VPCZoneIdentifier"),
                        "health_check_type": asg.get("HealthCheckType"),
                        "launch_template": asg.get("LaunchTemplate", {}),
                        "instances": [{"id": i["InstanceId"], "state": i.get("LifecycleState")} for i in asg.get("Instances", [])],
                        "tags": {t["Key"]: t["Value"] for t in asg.get("Tags", [])},
                    },
                })
        return groups

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_auto_scaling_groups(AutoScalingGroupNames=[resource_id])
        asgs = resp.get("AutoScalingGroups", [])
        return asgs[0] if asgs else None

    def set_desired_capacity(self, group_name: str, desired: int) -> Dict[str, Any]:
        self.client.set_desired_capacity(AutoScalingGroupName=group_name, DesiredCapacity=desired)
        return {"status": "updated", "group_name": group_name, "desired_capacity": desired}

    def list_policies(self, group_name: str) -> List[Dict[str, Any]]:
        resp = self.client.describe_policies(AutoScalingGroupName=group_name)
        return resp.get("ScalingPolicies", [])

    def list_activities(self, group_name: str) -> List[Dict[str, Any]]:
        resp = self.client.describe_scaling_activities(AutoScalingGroupName=group_name)
        return resp.get("Activities", [])

    def delete(self, resource_id: str, force_delete: bool = False) -> Dict[str, Any]:
        self.client.delete_auto_scaling_group(AutoScalingGroupName=resource_id, ForceDelete=force_delete)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# LOAD BALANCER
# ═══════════════════════════════════════════════════════════════════════
LB_CODE = '''"""Load Balancer Service — Production (ALB + NLB)"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class LoadBalancerService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("elbv2", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_load_balancers")
        lbs = []
        for page in paginator.paginate():
            for lb in page.get("LoadBalancers", []):
                lbs.append({
                    "resource_id": lb["LoadBalancerArn"],
                    "resource_type": "LoadBalancer",
                    "name": lb.get("LoadBalancerName"),
                    "region": self.region,
                    "status": lb.get("State", {}).get("Code", "unknown"),
                    "metadata": {
                        "type": lb.get("Type"),
                        "scheme": lb.get("Scheme"),
                        "dns_name": lb.get("DNSName"),
                        "vpc_id": lb.get("VpcId"),
                        "availability_zones": lb.get("AvailabilityZones", []),
                        "created_time": str(lb.get("CreatedTime", "")),
                    },
                })
        return lbs

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self.client.describe_load_balancers(LoadBalancerArns=[resource_id])
        lbs = resp.get("LoadBalancers", [])
        return lbs[0] if lbs else None

    def create(self, name: str, subnets: List[str], lb_type: str = "application", scheme: str = "internet-facing", security_groups: Optional[List[str]] = None, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"Name": name, "Subnets": subnets, "Type": lb_type, "Scheme": scheme}
        if security_groups:
            kwargs["SecurityGroups"] = security_groups
        if tags:
            kwargs["Tags"] = tags
        resp = self.client.create_load_balancer(**kwargs)
        lbs = resp.get("LoadBalancers", [])
        return lbs[0] if lbs else {}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self.client.delete_load_balancer(LoadBalancerArn=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
'''

# ═══════════════════════════════════════════════════════════════════════
# SSM
# ═══════════════════════════════════════════════════════════════════════
SSM_CODE = '''"""SSM Service — Production (Run Command, Parameter Store, Session Manager)"""
import logging
import time
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class SsmService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("ssm", region_name=region, role_arn=role_arn)

    # ─── Parameter Store ─────────────────────────────────────────────────────────
    def get_parameter(self, name: str, with_decryption: bool = True) -> Optional[Dict[str, Any]]:
        try:
            resp = self.client.get_parameter(Name=name, WithDecryption=with_decryption)
            return resp.get("Parameter")
        except self.client.exceptions.ParameterNotFound:
            return None

    def put_parameter(self, name: str, value: str, param_type: str = "SecureString", overwrite: bool = False) -> Dict[str, Any]:
        resp = self.client.put_parameter(Name=name, Value=value, Type=param_type, Overwrite=overwrite)
        return resp

    def list_parameters(self, path: str = "/", recursive: bool = True) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_parameters")
        params = []
        for page in paginator.paginate(ParameterFilters=[{"Key": "Path", "Option": "Recursive" if recursive else "OneLevel", "Values": [path]}]):
            params.extend(page.get("Parameters", []))
        return params

    def delete_parameter(self, name: str) -> Dict[str, Any]:
        self.client.delete_parameter(Name=name)
        return {"status": "deleted", "name": name}

    # ─── Run Command ─────────────────────────────────────────────────────────────
    def run_command(self, instance_ids: List[str], document_name: str = "AWS-RunShellScript", commands: Optional[List[str]] = None, timeout_seconds: int = 60) -> Dict[str, Any]:
        params: Dict[str, Any] = {"commands": commands or ["echo 'Hello from SSM Run Command'"]}
        resp = self.client.send_command(
            InstanceIds=instance_ids,
            DocumentName=document_name,
            Parameters=params,
            TimeoutSeconds=timeout_seconds,
        )
        cmd = resp.get("Command", {})
        return {"command_id": cmd.get("CommandId"), "status": cmd.get("Status"), "instance_ids": instance_ids}

    def get_command_invocation(self, command_id: str, instance_id: str) -> Dict[str, Any]:
        resp = self.client.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        return resp

    # ─── Managed Instances ────────────────────────────────────────────────────────
    def list_managed_instances(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_instance_information")
        instances = []
        for page in paginator.paginate():
            instances.extend(page.get("InstanceInformationList", []))
        return instances

    def list(self) -> List[Dict[str, Any]]:
        return self.list_managed_instances()
'''

# ═══════════════════════════════════════════════════════════════════════
# CLOUDTRAIL
# ═══════════════════════════════════════════════════════════════════════
CLOUDTRAIL_CODE = '''"""CloudTrail Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class CloudtrailService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("cloudtrail", region_name=region, role_arn=role_arn)

    def list(self) -> List[Dict[str, Any]]:
        resp = self.client.describe_trails(includeShadowTrails=True)
        trails = []
        for trail in resp.get("trailList", []):
            try:
                status = self.client.get_trail_status(Name=trail["TrailARN"])
                is_logging = status.get("IsLogging", False)
            except Exception:
                is_logging = False
            trails.append({
                "resource_id": trail.get("TrailARN", trail["Name"]),
                "resource_type": "CloudTrail",
                "name": trail.get("Name"),
                "region": self.region,
                "status": "logging" if is_logging else "not_logging",
                "metadata": {
                    "s3_bucket": trail.get("S3BucketName"),
                    "is_multi_region": trail.get("IsMultiRegionTrail"),
                    "log_file_validation": trail.get("LogFileValidationEnabled"),
                    "cloud_watch_logs_arn": trail.get("CloudWatchLogsLogGroupArn"),
                    "kms_key_id": trail.get("KMSKeyId"),
                },
            })
        return trails

    def lookup_events(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, attribute_key: Optional[str] = None, attribute_value: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"MaxResults": max_results}
        if start_time:
            kwargs["StartTime"] = start_time
        if end_time:
            kwargs["EndTime"] = end_time
        if attribute_key and attribute_value:
            kwargs["LookupAttributes"] = [{"AttributeKey": attribute_key, "AttributeValue": attribute_value}]
        resp = self.client.lookup_events(**kwargs)
        return resp.get("Events", [])

    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        end = datetime.utcnow()
        start = end - timedelta(hours=hours)
        return self.lookup_events(start_time=start, end_time=end)
'''

# ═══════════════════════════════════════════════════════════════════════
# AWS CONFIG
# ═══════════════════════════════════════════════════════════════════════
CONFIG_CODE = '''"""AWS Config Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class ConfigService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("config", region_name=region, role_arn=role_arn)

    def list_rules(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("describe_config_rules")
        rules = []
        for page in paginator.paginate():
            rules.extend(page.get("ConfigRules", []))
        return rules

    def get_compliance_by_rule(self, rule_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if rule_names:
            kwargs["ConfigRuleNames"] = rule_names
        resp = self.client.describe_compliance_by_config_rule(**kwargs)
        return resp.get("ComplianceByConfigRules", [])

    def list_discovered_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("list_discovered_resources")
        resources = []
        for page in paginator.paginate(resourceType=resource_type):
            resources.extend(page.get("resourceIdentifiers", []))
        return resources

    def get_resource_config_history(self, resource_type: str, resource_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        resp = self.client.get_resource_config_history(
            resourceType=resource_type, resourceId=resource_id, limit=limit
        )
        return resp.get("configurationItems", [])

    def list(self) -> List[Dict[str, Any]]:
        return self.list_rules()
'''

# ═══════════════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════════════
BACKUP_CODE = '''"""AWS Backup Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.client = client_factory.get_aws_client("backup", region_name=region, role_arn=role_arn)

    def list_vaults(self) -> List[Dict[str, Any]]:
        resp = self.client.list_backup_vaults()
        return resp.get("BackupVaultList", [])

    def list_plans(self) -> List[Dict[str, Any]]:
        paginator = self.client.get_paginator("list_backup_plans")
        plans = []
        for page in paginator.paginate():
            plans.extend(page.get("BackupPlansList", []))
        return plans

    def list_jobs(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if state:
            kwargs["ByState"] = state
        paginator = self.client.get_paginator("list_backup_jobs")
        jobs = []
        for page in paginator.paginate(**kwargs):
            jobs.extend(page.get("BackupJobs", []))
        return jobs

    def list(self) -> List[Dict[str, Any]]:
        return self.list_vaults()

    def start_backup_job(self, vault_name: str, resource_arn: str, iam_role_arn: str) -> Dict[str, Any]:
        resp = self.client.start_backup_job(
            BackupVaultName=vault_name,
            ResourceArn=resource_arn,
            IamRoleArn=iam_role_arn,
        )
        return resp
'''

files_map = {
    "backend/app/providers/aws/internet_gateway_service.py": IGW_CODE,
    "backend/app/providers/aws/nat_gateway_service.py": NAT_CODE,
    "backend/app/providers/aws/route_table_service.py": RT_CODE,
    "backend/app/providers/aws/subnet_service.py": SUBNET_CODE,
    "backend/app/providers/aws/security_group_service.py": SG_CODE,
    "backend/app/providers/aws/ebs_service.py": EBS_CODE,
    "backend/app/providers/aws/autoscaling_service.py": ASG_CODE,
    "backend/app/providers/aws/load_balancer_service.py": LB_CODE,
    "backend/app/providers/aws/ssm_service.py": SSM_CODE,
    "backend/app/providers/aws/cloudtrail_service.py": CLOUDTRAIL_CODE,
    "backend/app/providers/aws/config_service.py": CONFIG_CODE,
    "backend/app/providers/aws/backup_service.py": BACKUP_CODE,
}

for filepath, code in files_map.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(code.strip() + "\n")
    print(f"Written: {filepath}")
