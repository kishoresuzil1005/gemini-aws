from botocore.exceptions import ClientError
from botocore.exceptions import EndpointConnectionError
import boto3
import logging
from typing import Callable, Any

from app.providers.aws.regions import get_all_regions

logger = logging.getLogger(__name__)


class AWSRelationshipBuilder:
    # Relationship type constants
    IN_VPC = "IN_VPC"
    IN_SUBNET = "IN_SUBNET"
    USES_SECURITY_GROUP = "USES_SECURITY_GROUP"
    ATTACHED_VOLUME = "ATTACHED_VOLUME"
    ATTACHED_TO = "ATTACHED_TO"
    USES_ROLE = "USES_ROLE"
    ROUTES_TO = "ROUTES_TO"
    USES_TARGET_GROUP = "USES_TARGET_GROUP"
    TARGETS = "TARGETS"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    USES_ELASTIC_IP = "USES_ELASTIC_IP"
    MANAGES = "MANAGES"
    HAS_NODEGROUP = "HAS_NODEGROUP"

    def __init__(self):
        self.regions = get_all_regions()
        # Cache for boto3 clients
        self.clients = {}
        try:
            self.iam = self.get_client("iam")
        except (ClientError, EndpointConnectionError, Exception):
            logger.exception("Unable to initialize IAM client")
            self.iam = None

    def get_client(self, service: str, region: str = None) -> Any:
        key = (service, region)
        if key not in self.clients:
            kwargs = {}
            if region:
                kwargs["region_name"] = region
            self.clients[key] = boto3.client(service, **kwargs)
        return self.clients[key]

    def scan_regions(self, service: str, callback: Callable) -> list[dict]:
        relationships = []
        for region in self.regions:
            try:
                client = self.get_client(service, region)
                relationships.extend(callback(client, region))
            except ClientError:
                logger.exception("%s scan failed in %s", service, region)
            except EndpointConnectionError:
                logger.exception("%s scan failed in %s", service, region)
            except Exception:
                logger.exception("%s scan failed in %s", service, region)
        return relationships

    def relationship(
        self,
        source: str,
        target: str,
        rel_type: str,
        source_type: str,
        target_type: str
    ) -> dict:
        return {
            "from": source,
            "to": target,
            "type": rel_type,
            "source_type": source_type,
            "target_type": target_type
        }

    def build(self) -> list[dict]:
        relationships = []
        builders = [
            self.ec2_to_ebs,
            self.ec2_to_vpc,
            self.ec2_to_subnet,
            self.ec2_to_sg,
            self.subnet_to_vpc,
            self.sg_to_vpc,
            self.igw_to_vpc,
            self.rds_to_vpc,
            self.rds_to_subnet,
            self.rds_to_sg,
            self.ec2_to_iam,
            self.lambda_to_iam,
            self.lambda_to_vpc,
            self.lambda_to_subnet,
            self.lambda_to_sg,
            self.route_table_to_subnet,
            self.route_table_to_vpc,
            self.route_table_to_gateway,
            self.route_table_to_nat_gateway,
            self.nat_gateway_to_subnet,
            self.nat_gateway_to_eip,
            self.eni_to_ec2,
            self.eni_to_security_group,
            self.eni_to_subnet,
            self.eni_to_vpc,
            self.autoscaling_to_ec2,
            self.eks_cluster_to_nodegroup,
            self.nodegroup_to_ec2,
            self.alb_to_ec2,
            self.eip_to_resource,
        ]

        for builder in builders:
            try:
                relationships.extend(builder())
            except (ClientError, EndpointConnectionError, Exception):
                logger.exception("Relationship builder failed: %s", builder.__name__)

        # Remove duplicate relationships
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel["from"], rel["to"], rel["type"])
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)

        logger.info(
            "Discovered %d unique relationships (%d duplicates removed)",
            len(unique_relationships),
            len(relationships) - len(unique_relationships)
        )
        return unique_relationships

    def ec2_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        vpc = instance.get("VpcId")
                        if vpc:
                            rels.append(self.relationship(instance["InstanceId"], vpc, self.IN_VPC, "EC2", "VPC"))
            return rels
        return self.scan_regions("ec2", collect)

    def ec2_to_subnet(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        subnet = instance.get("SubnetId")
                        if subnet:
                            rels.append(self.relationship(instance["InstanceId"], subnet, self.IN_SUBNET, "EC2", "Subnet"))
            return rels
        return self.scan_regions("ec2", collect)

    def ec2_to_sg(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        for sg in instance.get("SecurityGroups", []):
                            rels.append(self.relationship(instance["InstanceId"], sg["GroupId"], self.USES_SECURITY_GROUP, "EC2", "SecurityGroup"))
            return rels
        return self.scan_regions("ec2", collect)

    def ec2_to_ebs(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        for mapping in instance.get("BlockDeviceMappings", []):
                            ebs = mapping.get("Ebs")
                            if ebs:
                                rels.append(self.relationship(instance["InstanceId"], ebs["VolumeId"], self.ATTACHED_VOLUME, "EC2", "EBS"))
            return rels
        return self.scan_regions("ec2", collect)

    def subnet_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            next_token = None
            while True:
                params = {}
                if next_token:
                    params["NextToken"] = next_token
                response = ec2.describe_subnets(**params)
                for subnet in response.get("Subnets", []):
                    rels.append(self.relationship(subnet["SubnetId"], subnet["VpcId"], self.IN_VPC, "Subnet", "VPC"))
                next_token = response.get("NextToken")
                if not next_token:
                    break
            return rels
        return self.scan_regions("ec2", collect)

    def sg_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            next_token = None
            while True:
                params = {}
                if next_token:
                    params["NextToken"] = next_token
                response = ec2.describe_security_groups(**params)
                for sg in response.get("SecurityGroups", []):
                    vpc = sg.get("VpcId")
                    if vpc:
                        rels.append(self.relationship(sg["GroupId"], vpc, self.IN_VPC, "SecurityGroup", "VPC"))
                next_token = response.get("NextToken")
                if not next_token:
                    break
            return rels
        return self.scan_regions("ec2", collect)

    def igw_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            next_token = None
            while True:
                params = {}
                if next_token:
                    params["NextToken"] = next_token
                response = ec2.describe_internet_gateways(**params)
                for igw in response.get("InternetGateways", []):
                    for attachment in igw.get("Attachments", []):
                        rels.append(self.relationship(igw["InternetGatewayId"], attachment["VpcId"], self.ATTACHED_TO, "InternetGateway", "VPC"))
                next_token = response.get("NextToken")
                if not next_token:
                    break
            return rels
        return self.scan_regions("ec2", collect)

    def rds_to_vpc(self) -> list[dict]:
        def collect(rds, region):
            rels = []
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page["DBInstances"]:
                    vpc_id = db.get("DBSubnetGroup", {}).get("VpcId")
                    if vpc_id:
                        rels.append(self.relationship(db["DBInstanceIdentifier"], vpc_id, self.IN_VPC, "RDS", "VPC"))
            return rels
        return self.scan_regions("rds", collect)

    def rds_to_subnet(self) -> list[dict]:
        def collect(rds, region):
            rels = []
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page["DBInstances"]:
                    rds_id = db["DBInstanceIdentifier"]
                    for subnet in db.get("DBSubnetGroup", {}).get("Subnets", []):
                        subnet_id = subnet.get("SubnetIdentifier")
                        if subnet_id:
                            rels.append(self.relationship(rds_id, subnet_id, self.IN_SUBNET, "RDS", "Subnet"))
            return rels
        return self.scan_regions("rds", collect)

    def rds_to_sg(self) -> list[dict]:
        def collect(rds, region):
            rels = []
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page["DBInstances"]:
                    rds_id = db["DBInstanceIdentifier"]
                    for sg in db.get("VpcSecurityGroups", []):
                        rels.append(self.relationship(rds_id, sg["VpcSecurityGroupId"], self.USES_SECURITY_GROUP, "RDS", "SecurityGroup"))
            return rels
        return self.scan_regions("rds", collect)

    def ec2_to_iam(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        profile = instance.get("IamInstanceProfile")
                        if not profile:
                            continue
                        profile_arn = profile.get("Arn")
                        if not profile_arn:
                            continue
                        
                        try:
                            profile_name = profile_arn.split("/")[-1]
                            if self.iam:
                                res = self.iam.get_instance_profile(
                                    InstanceProfileName=profile_name
                                )
                                roles = res.get("InstanceProfile", {}).get("Roles", [])
                                for role in roles:
                                    rels.append(self.relationship(instance["InstanceId"], role["Arn"], self.USES_ROLE, "EC2", "IAM"))
                        except Exception as e:
                            logger.warning(
                                "Failed to resolve IAM Role for instance profile %s: %s",
                                profile_arn, str(e)
                            )
            return rels
        return self.scan_regions("ec2", collect)

    def lambda_to_iam(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    role_arn = fn.get("Role")
                    if role_arn:
                        rels.append(self.relationship(fn["FunctionName"], role_arn, self.USES_ROLE, "Lambda", "IAM"))
            return rels
        return self.scan_regions("lambda", collect)

    def lambda_to_vpc(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    config = fn.get("VpcConfig", {})
                    vpc_id = config.get("VpcId")
                    if vpc_id:
                        rels.append(self.relationship(fn["FunctionName"], vpc_id, self.IN_VPC, "Lambda", "VPC"))
            return rels
        return self.scan_regions("lambda", collect)

    def lambda_to_subnet(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    config = fn.get("VpcConfig", {})
                    for subnet in config.get("SubnetIds", []):
                        rels.append(self.relationship(fn["FunctionName"], subnet, self.IN_SUBNET, "Lambda", "Subnet"))
            return rels
        return self.scan_regions("lambda", collect)

    def lambda_to_sg(self) -> list[dict]:
        def collect(lmb, region):
            rels = []
            for page in lmb.get_paginator("list_functions").paginate():
                for fn in page["Functions"]:
                    config = fn.get("VpcConfig", {})
                    for sg in config.get("SecurityGroupIds", []):
                        rels.append(self.relationship(fn["FunctionName"], sg, self.USES_SECURITY_GROUP, "Lambda", "SecurityGroup"))
            return rels
        return self.scan_regions("lambda", collect)

    def route_table_to_subnet(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_route_tables").paginate():
                for rt in page["RouteTables"]:
                    for assoc in rt.get("Associations", []):
                        subnet_id = assoc.get("SubnetId")
                        if subnet_id:
                            rels.append(self.relationship(rt["RouteTableId"], subnet_id, self.ASSOCIATED_WITH, "RouteTable", "Subnet"))
            return rels
        return self.scan_regions("ec2", collect)

    def route_table_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []

            for page in ec2.get_paginator(
                "describe_route_tables"
            ).paginate():

                for rt in page.get("RouteTables", []):

                    vpc_id = rt.get("VpcId")

                    if vpc_id:

                        rels.append(
                            self.relationship(rt["RouteTableId"], vpc_id, self.IN_VPC, "RouteTable", "VPC")
                        )

            return rels

        return self.scan_regions(
            "ec2",
            collect
        )

    def route_table_to_gateway(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_route_tables").paginate():
                for rt in page["RouteTables"]:
                    for route in rt.get("Routes", []):
                        gateway = route.get("GatewayId")
                        if gateway:
                            rels.append(self.relationship(rt["RouteTableId"], gateway, self.ROUTES_TO, "RouteTable", "InternetGateway"))
            return rels
        return self.scan_regions("ec2", collect)

    def route_table_to_nat_gateway(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_route_tables").paginate():
                for rt in page["RouteTables"]:
                    for route in rt.get("Routes", []):
                        nat = route.get("NatGatewayId")
                        if nat:
                            rels.append(self.relationship(rt["RouteTableId"], nat, self.ROUTES_TO, "RouteTable", "NatGateway"))
            return rels
        return self.scan_regions("ec2", collect)

    def nat_gateway_to_subnet(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_nat_gateways").paginate():
                for nat in page["NatGateways"]:
                    subnet = nat.get("SubnetId")
                    if subnet:
                        rels.append(self.relationship(nat["NatGatewayId"], subnet, self.IN_SUBNET, "NatGateway", "Subnet"))
            return rels
        return self.scan_regions("ec2", collect)

    def nat_gateway_to_eip(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_nat_gateways").paginate():
                for nat in page["NatGateways"]:
                    for address in nat.get("NatGatewayAddresses", []):
                        allocation = address.get("AllocationId")
                        if allocation:
                            rels.append(self.relationship(nat["NatGatewayId"], allocation, self.USES_ELASTIC_IP, "NatGateway", "ElasticIP"))
            return rels
        return self.scan_regions("ec2", collect)

    def eni_to_ec2(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_network_interfaces").paginate():
                for eni in page["NetworkInterfaces"]:
                    attachment = eni.get("Attachment")
                    if not attachment:
                        continue
                    instance_id = attachment.get("InstanceId")
                    if instance_id:
                        rels.append(self.relationship(eni["NetworkInterfaceId"], instance_id, self.ATTACHED_TO, "NetworkInterface", "EC2"))
            return rels
        return self.scan_regions("ec2", collect)

    def eni_to_security_group(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_network_interfaces").paginate():
                for eni in page["NetworkInterfaces"]:
                    eni_id = eni["NetworkInterfaceId"]
                    for sg in eni.get("Groups", []):
                        rels.append(self.relationship(eni_id, sg["GroupId"], self.USES_SECURITY_GROUP, "NetworkInterface", "SecurityGroup"))
            return rels
        return self.scan_regions("ec2", collect)

    def eni_to_subnet(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_network_interfaces").paginate():
                for eni in page["NetworkInterfaces"]:
                    subnet = eni.get("SubnetId")
                    if subnet:
                        rels.append(self.relationship(eni["NetworkInterfaceId"], subnet, self.IN_SUBNET, "NetworkInterface", "Subnet"))
            return rels
        return self.scan_regions("ec2", collect)

    def eni_to_vpc(self) -> list[dict]:
        def collect(ec2, region):
            rels = []
            for page in ec2.get_paginator("describe_network_interfaces").paginate():
                for eni in page["NetworkInterfaces"]:
                    vpc = eni.get("VpcId")
                    if vpc:
                        rels.append(self.relationship(eni["NetworkInterfaceId"], vpc, self.IN_VPC, "NetworkInterface", "VPC"))
            return rels
        return self.scan_regions("ec2", collect)

    def autoscaling_to_ec2(self) -> list[dict]:
        def collect(autoscaling, region):
            rels = []
            for page in autoscaling.get_paginator("describe_auto_scaling_groups").paginate():
                for group in page["AutoScalingGroups"]:
                    group_name = group["AutoScalingGroupName"]
                    for instance in group.get("Instances", []):
                        rels.append(self.relationship(group_name, instance["InstanceId"], self.MANAGES, "AutoScalingGroup", "EC2"))
            return rels
        return self.scan_regions("autoscaling", collect)

    def eks_cluster_to_nodegroup(self) -> list[dict]:
        def collect(eks, region):
            rels = []
            try:
                for cluster_page in eks.get_paginator("list_clusters").paginate():
                    for cluster_name in cluster_page.get("clusters", []):
                        for nodegroup_page in eks.get_paginator("list_nodegroups").paginate(clusterName=cluster_name):
                            for nodegroup in nodegroup_page.get("nodegroups", []):
                                rels.append(self.relationship(cluster_name, nodegroup, self.HAS_NODEGROUP, "EKSCluster", "NodeGroup"))
            except Exception:
                pass
            return rels
        return self.scan_regions("eks", collect)

    def nodegroup_to_ec2(self) -> list[dict]:
        def collect(eks, region):
            rels = []
            try:
                autoscaling = self.get_client("autoscaling", region)
                if not autoscaling:
                    return rels
                    
                for cluster_page in eks.get_paginator("list_clusters").paginate():
                    for cluster_name in cluster_page.get("clusters", []):
                        for nodegroup_page in eks.get_paginator("list_nodegroups").paginate(clusterName=cluster_name):
                            for nodegroup in nodegroup_page.get("nodegroups", []):
                                details = eks.describe_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup)
                                asgs = details.get("nodegroup", {}).get("resources", {}).get("autoScalingGroups", [])
                                for asg in asgs:
                                    group_name = asg.get("name")
                                    if not group_name:
                                        continue
                                    
                                    response = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[group_name])
                                    for group in response.get("AutoScalingGroups", []):
                                        for instance in group.get("Instances", []):
                                            rels.append(self.relationship(nodegroup, instance["InstanceId"], self.MANAGES, "NodeGroup", "EC2"))
            except Exception:
                pass
            return rels
        return self.scan_regions("eks", collect)

    def alb_to_ec2(self) -> list[dict]:
        def collect(elbv2, region):
            rels = []
            for page in elbv2.get_paginator("describe_load_balancers").paginate():
                for lb in page["LoadBalancers"]:
                    lb_arn = lb["LoadBalancerArn"]
                    for tg_page in elbv2.get_paginator("describe_target_groups").paginate(LoadBalancerArn=lb_arn):
                        for tg in tg_page["TargetGroups"]:
                            tg_arn = tg["TargetGroupArn"]
                            rels.append(self.relationship(lb_arn, tg_arn, self.USES_TARGET_GROUP, "ALB", "TargetGroup"))
                            
                            health = elbv2.describe_target_health(TargetGroupArn=tg_arn)
                            for target in health["TargetHealthDescriptions"]:
                                instance_id = target["Target"]["Id"]
                                rels.append(self.relationship(tg_arn, instance_id, self.TARGETS, "TargetGroup", "EC2"))
            return rels
        return self.scan_regions("elbv2", collect)

    def eip_to_resource(self):
        """
        Elastic IP
            ├── ASSIGNED_TO EC2
            ├── ASSIGNED_TO NetworkInterface
            └── ASSIGNED_TO NatGateway
        """

        relationships = []

        for region in self.regions:

            try:

                ec2 = self.get_client("ec2", region)

                addresses = ec2.describe_addresses()

                #
                # Build AllocationId -> NatGateway map
                #

                nat_map = {}

                try:

                    ngws = ec2.describe_nat_gateways()

                    for ngw in ngws.get("NatGateways", []):

                        nat_id = ngw.get("NatGatewayId")

                        for addr in ngw.get("NatGatewayAddresses", []):

                            allocation_id = addr.get("AllocationId")

                            if allocation_id:

                                nat_map[allocation_id] = nat_id

                except Exception:

                    logger.exception(
                        "Unable to discover NAT Gateways in %s",
                        region
                    )

                #
                # Elastic IP Relationships
                #

                for eip in addresses.get("Addresses", []):

                    allocation_id = eip.get("AllocationId")

                    #
                    # Elastic IP -> EC2
                    #

                    instance_id = eip.get("InstanceId")

                    if instance_id:

                        relationships.append(
                            {
                                "from": allocation_id,
                                "to": instance_id,
                                "type": "ASSIGNED_TO",
                                "source_type": "ElasticIP",
                                "target_type": "EC2"
                            }
                        )

                    #
                    # Elastic IP -> ENI
                    #

                    eni = eip.get("NetworkInterfaceId")

                    if eni:

                        relationships.append(
                            {
                                "from": allocation_id,
                                "to": eni,
                                "type": "ASSIGNED_TO",
                                "source_type": "ElasticIP",
                                "target_type": "NetworkInterface"
                            }
                        )

                    #
                    # Elastic IP -> NAT Gateway
                    #

                    if allocation_id in nat_map:

                        relationships.append(
                            {
                                "from": allocation_id,
                                "to": nat_map[allocation_id],
                                "type": "ASSIGNED_TO",
                                "source_type": "ElasticIP",
                                "target_type": "NatGateway"
                            }
                        )

            except Exception:

                logger.exception(
                    "Elastic IP relationship discovery failed in %s",
                    region
                )

        return relationships
