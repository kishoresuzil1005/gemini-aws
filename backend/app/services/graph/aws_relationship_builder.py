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
    HAS_SERVICE = "HAS_SERVICE"
    HAS_TASK = "HAS_TASK"
    RUNS_TASK = "RUNS_TASK"
    TARGETS_TASK = "TARGETS_TASK"
    HAS_CONTAINER = "HAS_CONTAINER"
    USES_CAPACITY_PROVIDER = "USES_CAPACITY_PROVIDER"
    USES_TASK_DEFINITION = "USES_TASK_DEFINITION"
    EXECUTION_ROLE = "EXECUTION_ROLE"
    TASK_ROLE = "TASK_ROLE"
    ATTACHED_TO_ENI = "ATTACHED_TO_ENI"
    RUNS_ON_CONTAINER_INSTANCE = "RUNS_ON_CONTAINER_INSTANCE"
    # Phase 4 constants
    FRONTED_BY = "FRONTED_BY"
    PROTECTED_BY = "PROTECTED_BY"
    RESOLVES_TO = "RESOLVES_TO"
    HAS_INTEGRATION = "HAS_INTEGRATION"
    INVOKES = "INVOKES"
    USES_SECRET = "USES_SECRET"
    ROTATED_BY = "ROTATED_BY"
    PUBLISHES_TO = "PUBLISHES_TO"
    SUBSCRIBES_TO = "SUBSCRIBES_TO"
    TRIGGERS = "TRIGGERS"
    SENDS_TO = "SENDS_TO"
    HAS_DLQ = "HAS_DLQ"
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    HAS_MOUNT_TARGET = "HAS_MOUNT_TARGET"
    MOUNTED_ON = "MOUNTED_ON"
    HAS_STREAM = "HAS_STREAM"
    HAS_STAGE = "HAS_STAGE"


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
            self.ecs_cluster_to_service,
            self.ecs_cluster_to_task,
            self.ecs_service_to_task_definition,
            self.ecs_service_to_task,
            self.ecs_task_to_subnet,
            self.ecs_task_to_vpc,
            self.ecs_task_to_security_group,
            self.ecs_task_to_eni,
            self.ecs_task_to_container_instance,
            self.task_definition_to_execution_role,
            self.task_definition_to_task_role,
            self.container_instance_to_ec2,
            self.target_group_to_task,
            self.ecs_task_to_task_definition,
            self.ecs_task_to_container,
            # Phase 4 builders
            self.apigateway_to_lambda,
            self.apigateway_to_alb,
            self.apigateway_to_vpc_link,
            self.apigateway_has_stage,
            self.cloudfront_to_s3,
            self.cloudfront_to_alb,
            self.cloudfront_to_apigateway,
            self.cloudfront_protected_by_waf,
            self.route53_to_cloudfront,
            self.route53_to_alb,
            self.route53_to_apigateway,
            self.route53_to_ec2,
            self.waf_to_alb,
            self.waf_to_apigateway,
            self.lambda_to_secret,
            self.rds_rotated_by_secret,
            self.lambda_to_sqs,
            self.sqs_has_dlq,
            self.lambda_to_dynamodb,
            self.ec2_to_elasticache,
            self.lambda_to_opensearch,
            self.opensearch_to_vpc,
            self.ec2_to_efs,
            self.efs_mount_to_subnet,
            self.sns_to_sqs,
            self.sns_to_lambda,
            self.eventbridge_to_lambda,
            self.eventbridge_to_ecs,
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

    def ecs_cluster_to_service(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in page.get("clusterArns", []):
                    for svc_page in ecs.get_paginator("list_services").paginate(cluster=cluster_arn):
                        for svc_arn in svc_page.get("serviceArns", []):
                            rels.append(self.relationship(cluster_arn, svc_arn, self.HAS_SERVICE, "ECSCluster", "ECSService"))
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_cluster_to_task(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        for task_arn in task_page.get("taskArns", []):
                            rels.append(self.relationship(cluster_arn, task_arn, self.HAS_TASK, "ECSCluster", "ECSTask"))
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_service_to_task_definition(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for svc_page in ecs.get_paginator("list_services").paginate(cluster=cluster_arn):
                        services = svc_page.get("serviceArns", [])
                        if services:
                            for i in range(0, len(services), 10):
                                chunk = services[i:i+10]
                                try:
                                    svc_resp = ecs.describe_services(cluster=cluster_arn, services=chunk)
                                    for svc in svc_resp.get("services", []):
                                        svc_arn = svc["serviceArn"]
                                        task_def = svc.get("taskDefinition")
                                        if task_def:
                                            rels.append(self.relationship(svc_arn, task_def, self.USES_TASK_DEFINITION, "ECSService", "ECSTaskDefinition"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_service_to_task(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        group = task.get("group", "")
                                        if group.startswith("service:"):
                                            svc_name = group.split("service:")[-1]
                                            region_acc = ":".join(cluster_arn.split(":")[3:5])
                                            c_name = cluster_arn.split("/")[-1]
                                            svc_arn = f"arn:aws:ecs:{region_acc}:service/{c_name}/{svc_name}"
                                            rels.append(self.relationship(svc_arn, task_arn, self.HAS_TASK, "ECSService", "ECSTask"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_subnet(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        for att in task.get("attachments", []):
                                            if att.get("type") == "ElasticNetworkInterface":
                                                for kv in att.get("details", []):
                                                    if kv.get("name") == "subnetId":
                                                        rels.append(self.relationship(task_arn, kv.get("value"), self.IN_SUBNET, "ECSTask", "Subnet"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_vpc(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        for att in task.get("attachments", []):
                                            if att.get("type") == "ElasticNetworkInterface":
                                                for kv in att.get("details", []):
                                                    if kv.get("name") == "vpcId":
                                                        rels.append(self.relationship(task_arn, kv.get("value"), self.IN_VPC, "ECSTask", "VPC"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_security_group(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        for att in task.get("attachments", []):
                                            if att.get("type") == "ElasticNetworkInterface":
                                                for kv in att.get("details", []):
                                                    if kv.get("name") == "securityGroups":
                                                        sgs = kv.get("value", "").split(",")
                                                        for sg in sgs:
                                                            if sg:
                                                                rels.append(self.relationship(task_arn, sg, self.USES_SECURITY_GROUP, "ECSTask", "SecurityGroup"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_eni(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        for att in task.get("attachments", []):
                                            if att.get("type") == "ElasticNetworkInterface":
                                                for kv in att.get("details", []):
                                                    if kv.get("name") == "networkInterfaceId":
                                                        rels.append(self.relationship(task_arn, kv.get("value"), self.ATTACHED_TO_ENI, "ECSTask", "NetworkInterface"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_container_instance(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        ci_arn = task.get("containerInstanceArn")
                                        if ci_arn:
                                            rels.append(self.relationship(task_arn, ci_arn, self.RUNS_ON_CONTAINER_INSTANCE, "ECSTask", "ECSContainerInstance"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def task_definition_to_execution_role(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for page in ecs.get_paginator("list_task_definitions").paginate():
                for td_arn in page.get("taskDefinitionArns", []):
                    try:
                        td_resp = ecs.describe_task_definition(taskDefinition=td_arn)
                        td = td_resp.get("taskDefinition", {})
                        er_arn = td.get("executionRoleArn")
                        if er_arn:
                            rels.append(self.relationship(td_arn, er_arn, self.EXECUTION_ROLE, "ECSTaskDefinition", "IAM"))
                    except Exception:
                        pass
            return rels
        return self.scan_regions("ecs", collect)

    def task_definition_to_task_role(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for page in ecs.get_paginator("list_task_definitions").paginate():
                for td_arn in page.get("taskDefinitionArns", []):
                    try:
                        td_resp = ecs.describe_task_definition(taskDefinition=td_arn)
                        td = td_resp.get("taskDefinition", {})
                        tr_arn = td.get("taskRoleArn")
                        if tr_arn:
                            rels.append(self.relationship(td_arn, tr_arn, self.TASK_ROLE, "ECSTaskDefinition", "IAM"))
                    except Exception:
                        pass
            return rels
        return self.scan_regions("ecs", collect)

    def container_instance_to_ec2(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for ci_page in ecs.get_paginator("list_container_instances").paginate(cluster=cluster_arn):
                        cis = ci_page.get("containerInstanceArns", [])
                        if cis:
                            for i in range(0, len(cis), 100):
                                chunk = cis[i:i+100]
                                try:
                                    ci_resp = ecs.describe_container_instances(cluster=cluster_arn, containerInstances=chunk)
                                    for ci in ci_resp.get("containerInstances", []):
                                        ci_arn = ci["containerInstanceArn"]
                                        ec2_id = ci.get("ec2InstanceId")
                                        if ec2_id:
                                            rels.append(self.relationship(ci_arn, ec2_id, self.ATTACHED_TO, "ECSContainerInstance", "EC2"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for svc_page in ecs.get_paginator("list_services").paginate(cluster=cluster_arn):
                        services = svc_page.get("serviceArns", [])
                        if services:
                            for i in range(0, len(services), 10):
                                chunk = services[i:i+10]
                                try:
                                    svc_resp = ecs.describe_services(cluster=cluster_arn, services=chunk)
                                    for svc in svc_resp.get("services", []):
                                        svc_arn = svc["serviceArn"]
                                        for lb in svc.get("loadBalancers", []):
                                            tg_arn = lb.get("targetGroupArn")
                                            if tg_arn:
                                                rels.append(self.relationship(tg_arn, svc_arn, self.TARGETS, "TargetGroup", "ECSService"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def target_group_to_task(self) -> list[dict]:
        def collect(ecs, region):
            import boto3
            rels = []
            try:
                elbv2 = boto3.client("elbv2", region_name=region)
                ip_to_task = {}
                for cluster_page in ecs.get_paginator("list_clusters").paginate():
                    for cluster_arn in cluster_page.get("clusterArns", []):
                        for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                            tasks = task_page.get("taskArns", [])
                            if tasks:
                                for i in range(0, len(tasks), 100):
                                    chunk = tasks[i:i+100]
                                    try:
                                        task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                        for task in task_resp.get("tasks", []):
                                            task_arn = task["taskArn"]
                                            for att in task.get("attachments", []):
                                                if att.get("type") == "ElasticNetworkInterface":
                                                    for kv in att.get("details", []):
                                                        if kv.get("name") == "privateIPv4Address":
                                                            ip_to_task[kv.get("value")] = task_arn
                                    except Exception:
                                        pass

                for tg_page in elbv2.get_paginator("describe_target_groups").paginate():
                    for tg in tg_page.get("TargetGroups", []):
                        tg_arn = tg["TargetGroupArn"]
                        try:
                            health_resp = elbv2.describe_target_health(TargetGroupArn=tg_arn)
                            for th in health_resp.get("TargetHealthDescriptions", []):
                                target_id = th["Target"]["Id"]
                                if target_id in ip_to_task:
                                    rels.append(self.relationship(tg_arn, ip_to_task[target_id], self.TARGETS_TASK, "TargetGroup", "ECSTask"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_task_definition(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        td_arn = task.get("taskDefinitionArn")
                                        if td_arn:
                                            rels.append(self.relationship(task_arn, td_arn, self.USES_TASK_DEFINITION, "ECSTask", "ECSTaskDefinition"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    def ecs_task_to_container(self) -> list[dict]:
        def collect(ecs, region):
            rels = []
            for cluster_page in ecs.get_paginator("list_clusters").paginate():
                for cluster_arn in cluster_page.get("clusterArns", []):
                    for task_page in ecs.get_paginator("list_tasks").paginate(cluster=cluster_arn):
                        tasks = task_page.get("taskArns", [])
                        if tasks:
                            for i in range(0, len(tasks), 100):
                                chunk = tasks[i:i+100]
                                try:
                                    task_resp = ecs.describe_tasks(cluster=cluster_arn, tasks=chunk)
                                    for task in task_resp.get("tasks", []):
                                        task_arn = task["taskArn"]
                                        for container in task.get("containers", []):
                                            c_arn = container.get("containerArn")
                                            if c_arn:
                                                rels.append(self.relationship(task_arn, c_arn, self.HAS_CONTAINER, "ECSTask", "ECSContainer"))
                                except Exception:
                                    pass
            return rels
        return self.scan_regions("ecs", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — API Gateway
    # ─────────────────────────────────────────────────────────────────────────

    def apigateway_to_lambda(self) -> list[dict]:
        """REST API integration → Lambda."""
        def collect(client, region):
            rels = []
            try:
                apigw = boto3.client("apigateway", region_name=region)
                paginator = apigw.get_paginator("get_rest_apis")
                for page in paginator.paginate():
                    for api in page.get("items", []):
                        api_id = api["id"]
                        try:
                            resources_resp = apigw.get_resources(restApiId=api_id, limit=500)
                            for resource in resources_resp.get("items", []):
                                for method in resource.get("resourceMethods", {}).values():
                                    try:
                                        integ = apigw.get_integration(
                                            restApiId=api_id,
                                            resourceId=resource["id"],
                                            httpMethod=method.get("httpMethod", "GET")
                                        )
                                        uri = integ.get("uri", "")
                                        if "lambda" in uri.lower():
                                            fn_arn = uri.split("functions/")[-1].split("/invocations")[0]
                                            rels.append(self.relationship(api_id, fn_arn, self.INVOKES, "APIGateway", "Lambda"))
                                    except Exception:
                                        pass
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                apigwv2 = boto3.client("apigatewayv2", region_name=region)
                paginator2 = apigwv2.get_paginator("get_apis")
                for page in paginator2.paginate():
                    for api in page.get("Items", []):
                        api_id = api["ApiId"]
                        try:
                            integ_pag = apigwv2.get_paginator("get_integrations")
                            for ipg in integ_pag.paginate(ApiId=api_id):
                                for integ in ipg.get("Items", []):
                                    uri = integ.get("IntegrationUri", "")
                                    if "lambda" in uri.lower():
                                        fn_arn = uri.split("functions/")[-1].split("/invocations")[0]
                                        rels.append(self.relationship(api_id, fn_arn, self.INVOKES, "APIGateway", "Lambda"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    def apigateway_to_alb(self) -> list[dict]:
        """HTTP API VPC integration → ALB."""
        def collect(client, region):
            rels = []
            try:
                apigwv2 = boto3.client("apigatewayv2", region_name=region)
                pag = apigwv2.get_paginator("get_apis")
                for page in pag.paginate():
                    for api in page.get("Items", []):
                        api_id = api["ApiId"]
                        try:
                            ipag = apigwv2.get_paginator("get_integrations")
                            for ipg in ipag.paginate(ApiId=api_id):
                                for integ in ipg.get("Items", []):
                                    uri = integ.get("IntegrationUri", "")
                                    if "elasticloadbalancing" in uri:
                                        rels.append(self.relationship(api_id, uri, self.HAS_INTEGRATION, "APIGateway", "ALB"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    def apigateway_to_vpc_link(self) -> list[dict]:
        """API Gateway → VPC Link."""
        def collect(client, region):
            rels = []
            try:
                apigwv2 = boto3.client("apigatewayv2", region_name=region)
                pag = apigwv2.get_paginator("get_vpc_links")
                for page in pag.paginate():
                    for link in page.get("Items", []):
                        link_id = link["VpcLinkId"]
                        for subnet in link.get("SubnetIds", []):
                            rels.append(self.relationship(link_id, subnet, self.IN_SUBNET, "VPCLink", "Subnet"))
                        for sg in link.get("SecurityGroupIds", []):
                            rels.append(self.relationship(link_id, sg, self.USES_SECURITY_GROUP, "VPCLink", "SecurityGroup"))
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    def apigateway_has_stage(self) -> list[dict]:
        """REST API → Stage."""
        def collect(client, region):
            rels = []
            try:
                apigw = boto3.client("apigateway", region_name=region)
                pag = apigw.get_paginator("get_rest_apis")
                for page in pag.paginate():
                    for api in page.get("items", []):
                        api_id = api["id"]
                        try:
                            stages = apigw.get_stages(restApiId=api_id)
                            for stage in stages.get("item", []):
                                stage_id = f"{api_id}/{stage['stageName']}"
                                rels.append(self.relationship(api_id, stage_id, self.HAS_STAGE, "APIGateway", "APIGatewayStage"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — CloudFront
    # ─────────────────────────────────────────────────────────────────────────

    def cloudfront_to_s3(self) -> list[dict]:
        rels = []
        try:
            cf = boto3.client("cloudfront", region_name="us-east-1")
            pag = cf.get_paginator("list_distributions")
            for page in pag.paginate():
                for dist in page.get("DistributionList", {}).get("Items", []):
                    dist_id = dist["Id"]
                    for origin in dist.get("Origins", {}).get("Items", []):
                        domain = origin.get("DomainName", "")
                        if ".s3." in domain or domain.endswith(".s3.amazonaws.com"):
                            bucket_name = domain.split(".s3.")[0]
                            rels.append(self.relationship(dist_id, f"s3-{bucket_name}", self.FRONTED_BY, "CloudFront", "S3"))
        except Exception:
            logger.exception("CloudFront → S3 relationship failed")
        return rels

    def cloudfront_to_alb(self) -> list[dict]:
        rels = []
        try:
            cf = boto3.client("cloudfront", region_name="us-east-1")
            elbv2 = boto3.client("elbv2", region_name="us-east-1")
            # Build a DNS → ARN map for ALBs
            alb_dns_map = {}
            for page in elbv2.get_paginator("describe_load_balancers").paginate():
                for lb in page.get("LoadBalancers", []):
                    alb_dns_map[lb["DNSName"].lower()] = lb["LoadBalancerArn"]

            for page in cf.get_paginator("list_distributions").paginate():
                for dist in page.get("DistributionList", {}).get("Items", []):
                    dist_id = dist["Id"]
                    for origin in dist.get("Origins", {}).get("Items", []):
                        domain = origin.get("DomainName", "").lower().rstrip(".")
                        if domain in alb_dns_map:
                            rels.append(self.relationship(dist_id, alb_dns_map[domain], self.FRONTED_BY, "CloudFront", "ALB"))
        except Exception:
            logger.exception("CloudFront → ALB relationship failed")
        return rels

    def cloudfront_to_apigateway(self) -> list[dict]:
        rels = []
        try:
            cf = boto3.client("cloudfront", region_name="us-east-1")
            for page in cf.get_paginator("list_distributions").paginate():
                for dist in page.get("DistributionList", {}).get("Items", []):
                    dist_id = dist["Id"]
                    for origin in dist.get("Origins", {}).get("Items", []):
                        domain = origin.get("DomainName", "")
                        if ".execute-api." in domain:
                            api_id = domain.split(".")[0]
                            rels.append(self.relationship(dist_id, api_id, self.FRONTED_BY, "CloudFront", "APIGateway"))
        except Exception:
            logger.exception("CloudFront → APIGateway relationship failed")
        return rels

    def cloudfront_protected_by_waf(self) -> list[dict]:
        rels = []
        try:
            cf = boto3.client("cloudfront", region_name="us-east-1")
            for page in cf.get_paginator("list_distributions").paginate():
                for dist in page.get("DistributionList", {}).get("Items", []):
                    dist_id = dist["Id"]
                    web_acl_id = dist.get("WebACLId", "")
                    if web_acl_id:
                        rels.append(self.relationship(dist_id, web_acl_id, self.PROTECTED_BY, "CloudFront", "WAFWebACL"))
        except Exception:
            logger.exception("CloudFront → WAF relationship failed")
        return rels

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — Route53
    # ─────────────────────────────────────────────────────────────────────────

    def _route53_records_to_resource(self, target_domain_check, target_type, rel_type):
        """Generic helper: scan all alias/CNAME records that match a domain pattern."""
        rels = []
        try:
            r53 = boto3.client("route53", region_name="us-east-1")
            elbv2 = boto3.client("elbv2", region_name="us-east-1") if target_type == "ALB" else None

            # Build ALB dns → ARN map
            alb_dns_map = {}
            if elbv2:
                for page in elbv2.get_paginator("describe_load_balancers").paginate():
                    for lb in page.get("LoadBalancers", []):
                        alb_dns_map[lb["DNSName"].lower().rstrip(".")] = lb["LoadBalancerArn"]

            for page in r53.get_paginator("list_hosted_zones").paginate():
                for zone in page.get("HostedZones", []):
                    zone_id = zone["Id"].split("/")[-1]
                    record_pag = r53.get_paginator("list_resource_record_sets")
                    for rpage in record_pag.paginate(HostedZoneId=zone_id):
                        for record in rpage.get("ResourceRecordSets", []):
                            alias_dns = record.get("AliasTarget", {}).get("DNSName", "").lower().rstrip(".")
                            record_id = f"{zone_id}/{record.get('Name', '').rstrip('.')}/{record.get('Type')}"

                            if target_domain_check(alias_dns):
                                if target_type == "ALB" and alias_dns in alb_dns_map:
                                    rels.append(self.relationship(record_id, alb_dns_map[alias_dns], rel_type, "Route53Record", "ALB"))
                                elif target_type == "CloudFront" and "cloudfront.net" in alias_dns:
                                    dist_domain = alias_dns.rstrip(".")
                                    rels.append(self.relationship(record_id, dist_domain, rel_type, "Route53Record", "CloudFront"))
                                elif target_type == "APIGateway" and ".execute-api." in alias_dns:
                                    api_id = alias_dns.split(".")[0]
                                    rels.append(self.relationship(record_id, api_id, rel_type, "Route53Record", "APIGateway"))
        except Exception:
            logger.exception("Route53 relationship scan failed")
        return rels

    def route53_to_cloudfront(self) -> list[dict]:
        return self._route53_records_to_resource(
            lambda d: "cloudfront.net" in d, "CloudFront", self.RESOLVES_TO
        )

    def route53_to_alb(self) -> list[dict]:
        return self._route53_records_to_resource(
            lambda d: "elb.amazonaws.com" in d or "elasticloadbalancing" in d, "ALB", self.RESOLVES_TO
        )

    def route53_to_apigateway(self) -> list[dict]:
        return self._route53_records_to_resource(
            lambda d: ".execute-api." in d, "APIGateway", self.RESOLVES_TO
        )

    def route53_to_ec2(self) -> list[dict]:
        """A records pointing directly to EC2 public IPs."""
        rels = []
        try:
            r53 = boto3.client("route53", region_name="us-east-1")
            # Build IP → instance map for current region
            ec2 = boto3.client("ec2", region_name="us-east-1")
            ip_map = {}
            for page in ec2.get_paginator("describe_instances").paginate():
                for res in page.get("Reservations", []):
                    for inst in res.get("Instances", []):
                        pub_ip = inst.get("PublicIpAddress")
                        if pub_ip:
                            ip_map[pub_ip] = inst["InstanceId"]

            for page in r53.get_paginator("list_hosted_zones").paginate():
                for zone in page.get("HostedZones", []):
                    zone_id = zone["Id"].split("/")[-1]
                    for rpage in r53.get_paginator("list_resource_record_sets").paginate(HostedZoneId=zone_id):
                        for record in rpage.get("ResourceRecordSets", []):
                            if record.get("Type") != "A":
                                continue
                            for rr in record.get("ResourceRecords", []):
                                ip = rr.get("Value", "")
                                if ip in ip_map:
                                    record_id = f"{zone_id}/{record.get('Name','').rstrip('.')}/A"
                                    rels.append(self.relationship(record_id, ip_map[ip], self.RESOLVES_TO, "Route53Record", "EC2"))
        except Exception:
            logger.exception("Route53 → EC2 relationship failed")
        return rels

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — WAF
    # ─────────────────────────────────────────────────────────────────────────

    def waf_to_alb(self) -> list[dict]:
        def collect(client, region):
            rels = []
            try:
                waf = boto3.client("wafv2", region_name=region)
                for scope in ("REGIONAL",):
                    for page in waf.get_paginator("list_web_acls").paginate(Scope=scope):
                        for acl in page.get("WebACLs", []):
                            acl_arn = acl["ARN"]
                            try:
                                assoc = waf.list_resources_for_web_acl(
                                    WebACLArn=acl_arn,
                                    ResourceType="APPLICATION_LOAD_BALANCER"
                                )
                                for res_arn in assoc.get("ResourceArns", []):
                                    rels.append(self.relationship(acl_arn, res_arn, self.PROTECTED_BY, "WAFWebACL", "ALB"))
                            except Exception:
                                pass
            except Exception:
                pass
            return rels
        return self.scan_regions("wafv2", collect)

    def waf_to_apigateway(self) -> list[dict]:
        def collect(client, region):
            rels = []
            try:
                waf = boto3.client("wafv2", region_name=region)
                for page in waf.get_paginator("list_web_acls").paginate(Scope="REGIONAL"):
                    for acl in page.get("WebACLs", []):
                        acl_arn = acl["ARN"]
                        try:
                            assoc = waf.list_resources_for_web_acl(
                                WebACLArn=acl_arn,
                                ResourceType="API_GATEWAY"
                            )
                            for res_arn in assoc.get("ResourceArns", []):
                                api_id = res_arn.split("/restapis/")[-1].split("/")[0] if "/restapis/" in res_arn else res_arn
                                rels.append(self.relationship(acl_arn, api_id, self.PROTECTED_BY, "WAFWebACL", "APIGateway"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("wafv2", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — Secrets Manager
    # ─────────────────────────────────────────────────────────────────────────

    def lambda_to_secret(self) -> list[dict]:
        """Lambda → Secret via resource policy or tags."""
        def collect(lam, region):
            rels = []
            try:
                sm = boto3.client("secretsmanager", region_name=region)
                for page in sm.get_paginator("list_secrets").paginate():
                    for secret in page.get("SecretList", []):
                        secret_arn = secret["ARN"]
                        tags = {t["Key"]: t["Value"] for t in secret.get("Tags", [])}
                        lambda_fn = tags.get("LambdaFunction") or tags.get("lambda_function")
                        if lambda_fn:
                            rels.append(self.relationship(lambda_fn, secret_arn, self.USES_SECRET, "Lambda", "Secret"))
                        # Also check rotation Lambda
                        rot_arn = secret.get("RotationLambdaARN", "")
                        if rot_arn:
                            rels.append(self.relationship(rot_arn, secret_arn, self.ROTATED_BY, "Lambda", "Secret"))
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    def rds_rotated_by_secret(self) -> list[dict]:
        """Secret → RDS via description/tag convention."""
        def collect(sm, region):
            rels = []
            try:
                for page in sm.get_paginator("list_secrets").paginate():
                    for secret in page.get("SecretList", []):
                        secret_arn = secret["ARN"]
                        owning = secret.get("OwningService", "")
                        if "rds" in owning.lower():
                            name = secret.get("Name", "")
                            db_id = name.split("/")[-1] if "/" in name else ""
                            if db_id:
                                rels.append(self.relationship(secret_arn, db_id, self.ROTATED_BY, "Secret", "RDS"))
            except Exception:
                pass
            return rels
        return self.scan_regions("secretsmanager", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — SQS
    # ─────────────────────────────────────────────────────────────────────────

    def lambda_to_sqs(self) -> list[dict]:
        """Lambda → SQS via event source mappings."""
        def collect(lam, region):
            rels = []
            try:
                for page in lam.get_paginator("list_event_source_mappings").paginate():
                    for mapping in page.get("EventSourceMappings", []):
                        source_arn = mapping.get("EventSourceArn", "")
                        fn_arn = mapping.get("FunctionArn", "")
                        if ":sqs:" in source_arn and fn_arn:
                            rels.append(self.relationship(source_arn, fn_arn, self.TRIGGERS, "SQSQueue", "Lambda"))
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    def sqs_has_dlq(self) -> list[dict]:
        """SQS Queue → DLQ."""
        def collect(sqs, region):
            import json
            rels = []
            try:
                for page in sqs.get_paginator("list_queues").paginate():
                    for queue_url in page.get("QueueUrls", []):
                        try:
                            attrs = sqs.get_queue_attributes(
                                QueueUrl=queue_url,
                                AttributeNames=["QueueArn", "RedrivePolicy"]
                            ).get("Attributes", {})
                            redrive = json.loads(attrs.get("RedrivePolicy", "{}"))
                            dlq_arn = redrive.get("deadLetterTargetArn", "")
                            if dlq_arn:
                                rels.append(self.relationship(attrs.get("QueueArn", queue_url), dlq_arn, self.HAS_DLQ, "SQSQueue", "SQSQueue"))
                        except Exception:
                            pass
            except Exception:
                pass
            return rels
        return self.scan_regions("sqs", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — SNS
    # ─────────────────────────────────────────────────────────────────────────

    def sns_to_sqs(self) -> list[dict]:
        """SNS Topic → SQS Subscription."""
        def collect(sns, region):
            rels = []
            try:
                for page in sns.get_paginator("list_subscriptions").paginate():
                    for sub in page.get("Subscriptions", []):
                        if sub.get("Protocol") == "sqs" and sub.get("SubscriptionArn") not in ("PendingConfirmation", "Deleted"):
                            rels.append(self.relationship(sub["TopicArn"], sub["Endpoint"], self.PUBLISHES_TO, "SNSTopic", "SQSQueue"))
            except Exception:
                pass
            return rels
        return self.scan_regions("sns", collect)

    def sns_to_lambda(self) -> list[dict]:
        """SNS Topic → Lambda Subscription."""
        def collect(sns, region):
            rels = []
            try:
                for page in sns.get_paginator("list_subscriptions").paginate():
                    for sub in page.get("Subscriptions", []):
                        if sub.get("Protocol") == "lambda" and sub.get("SubscriptionArn") not in ("PendingConfirmation", "Deleted"):
                            rels.append(self.relationship(sub["TopicArn"], sub["Endpoint"], self.TRIGGERS, "SNSTopic", "Lambda"))
            except Exception:
                pass
            return rels
        return self.scan_regions("sns", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — EventBridge
    # ─────────────────────────────────────────────────────────────────────────

    def eventbridge_to_lambda(self) -> list[dict]:
        def collect(eb, region):
            rels = []
            try:
                for bus_page in eb.get_paginator("list_event_buses").paginate():
                    for bus in bus_page.get("EventBuses", []):
                        bus_name = bus["Name"]
                        for rule_page in eb.get_paginator("list_rules").paginate(EventBusName=bus_name):
                            for rule in rule_page.get("Rules", []):
                                rule_name = rule["Name"]
                                rule_arn = rule["Arn"]
                                try:
                                    targets = eb.list_targets_by_rule(Rule=rule_name, EventBusName=bus_name)
                                    for t in targets.get("Targets", []):
                                        if ":lambda:" in t.get("Arn", ""):
                                            rels.append(self.relationship(rule_arn, t["Arn"], self.TRIGGERS, "EventBridgeRule", "Lambda"))
                                except Exception:
                                    pass
            except Exception:
                pass
            return rels
        return self.scan_regions("events", collect)

    def eventbridge_to_ecs(self) -> list[dict]:
        def collect(eb, region):
            rels = []
            try:
                for bus_page in eb.get_paginator("list_event_buses").paginate():
                    for bus in bus_page.get("EventBuses", []):
                        bus_name = bus["Name"]
                        for rule_page in eb.get_paginator("list_rules").paginate(EventBusName=bus_name):
                            for rule in rule_page.get("Rules", []):
                                rule_name = rule["Name"]
                                rule_arn = rule["Arn"]
                                try:
                                    targets = eb.list_targets_by_rule(Rule=rule_name, EventBusName=bus_name)
                                    for t in targets.get("Targets", []):
                                        if ":ecs:" in t.get("Arn", ""):
                                            rels.append(self.relationship(rule_arn, t["Arn"], self.TRIGGERS, "EventBridgeRule", "ECSCluster"))
                                except Exception:
                                    pass
            except Exception:
                pass
            return rels
        return self.scan_regions("events", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — DynamoDB
    # ─────────────────────────────────────────────────────────────────────────

    def lambda_to_dynamodb(self) -> list[dict]:
        """Lambda → DynamoDB via event source mappings (Streams)."""
        def collect(lam, region):
            rels = []
            try:
                for page in lam.get_paginator("list_event_source_mappings").paginate():
                    for mapping in page.get("EventSourceMappings", []):
                        source_arn = mapping.get("EventSourceArn", "")
                        fn_arn = mapping.get("FunctionArn", "")
                        if ":dynamodb:" in source_arn and fn_arn:
                            table_arn = source_arn.split("/stream/")[0]
                            rels.append(self.relationship(fn_arn, table_arn, self.READS_FROM, "Lambda", "DynamoDBTable"))
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — ElastiCache
    # ─────────────────────────────────────────────────────────────────────────

    def ec2_to_elasticache(self) -> list[dict]:
        """EC2/Lambda in same subnet group as ElastiCache (inferred by security group overlap)."""
        def collect(ec, region):
            rels = []
            try:
                # ElastiCache clusters → SG list
                for page in ec.get_paginator("describe_cache_clusters").paginate(ShowCacheNodeInfo=True):
                    for cluster in page.get("CacheClusters", []):
                        cluster_id = cluster["CacheClusterId"]
                        sg_ids = [sg["SecurityGroupId"] for sg in cluster.get("SecurityGroups", [])]
                        ec2_client = boto3.client("ec2", region_name=region)
                        if sg_ids:
                            for sg_id in sg_ids:
                                try:
                                    insts = ec2_client.describe_instances(
                                        Filters=[{"Name": "instance.group-id", "Values": [sg_id]}]
                                    )
                                    for res in insts.get("Reservations", []):
                                        for inst in res.get("Instances", []):
                                            rels.append(self.relationship(inst["InstanceId"], cluster_id, self.READS_FROM, "EC2", "ElastiCacheRedis"))
                                except Exception:
                                    pass
            except Exception:
                pass
            return rels
        return self.scan_regions("elasticache", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — OpenSearch
    # ─────────────────────────────────────────────────────────────────────────

    def lambda_to_opensearch(self) -> list[dict]:
        """Lambda → OpenSearch via event source mappings."""
        def collect(lam, region):
            rels = []
            try:
                for page in lam.get_paginator("list_event_source_mappings").paginate():
                    for mapping in page.get("EventSourceMappings", []):
                        source_arn = mapping.get("EventSourceArn", "")
                        fn_arn = mapping.get("FunctionArn", "")
                        if ":opensearch:" in source_arn or ":es:" in source_arn:
                            rels.append(self.relationship(fn_arn, source_arn, self.WRITES_TO, "Lambda", "OpenSearchDomain"))
            except Exception:
                pass
            return rels
        return self.scan_regions("lambda", collect)

    def opensearch_to_vpc(self) -> list[dict]:
        def collect(os_client, region):
            rels = []
            try:
                pag = os_client.get_paginator("list_domain_names")
                domain_names = []
                for page in pag.paginate():
                    domain_names.extend([d["DomainName"] for d in page.get("DomainNames", [])])
                for i in range(0, len(domain_names), 5):
                    chunk = domain_names[i:i+5]
                    resp = os_client.describe_domains(DomainNames=chunk)
                    for domain in resp.get("DomainStatusList", []):
                        arn = domain.get("ARN", domain["DomainName"])
                        vpc = domain.get("VPCOptions", {}).get("VPCId")
                        if vpc:
                            rels.append(self.relationship(arn, vpc, self.IN_VPC, "OpenSearchDomain", "VPC"))
                        for subnet in domain.get("VPCOptions", {}).get("SubnetIds", []):
                            rels.append(self.relationship(arn, subnet, self.IN_SUBNET, "OpenSearchDomain", "Subnet"))
                        for sg in domain.get("VPCOptions", {}).get("SecurityGroupIds", []):
                            rels.append(self.relationship(arn, sg, self.USES_SECURITY_GROUP, "OpenSearchDomain", "SecurityGroup"))
            except Exception:
                pass
            return rels
        return self.scan_regions("opensearch", collect)

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — EFS
    # ─────────────────────────────────────────────────────────────────────────

    def ec2_to_efs(self) -> list[dict]:
        """EC2 in same VPC as EFS Mount Target → EFS (inferred by subnet)."""
        def collect(efs_client, region):
            rels = []
            try:
                for page in efs_client.get_paginator("describe_file_systems").paginate():
                    for fs in page.get("FileSystems", []):
                        fs_id = fs["FileSystemId"]
                        fs_arn = fs.get("FileSystemArn", fs_id)
                        mt_pag = efs_client.get_paginator("describe_mount_targets")
                        for mt_page in mt_pag.paginate(FileSystemId=fs_id):
                            for mt in mt_page.get("MountTargets", []):
                                subnet_id = mt.get("SubnetId", "")
                                if subnet_id:
                                    ec2 = boto3.client("ec2", region_name=region)
                                    try:
                                        insts = ec2.describe_instances(
                                            Filters=[{"Name": "subnet-id", "Values": [subnet_id]}]
                                        )
                                        for res in insts.get("Reservations", []):
                                            for inst in res.get("Instances", []):
                                                rels.append(self.relationship(inst["InstanceId"], fs_arn, self.MOUNTED_ON, "EC2", "EFSFileSystem"))
                                    except Exception:
                                        pass
            except Exception:
                pass
            return rels
        return self.scan_regions("efs", collect)

    def efs_mount_to_subnet(self) -> list[dict]:
        def collect(efs_client, region):
            rels = []
            try:
                for page in efs_client.get_paginator("describe_file_systems").paginate():
                    for fs in page.get("FileSystems", []):
                        fs_id = fs["FileSystemId"]
                        fs_arn = fs.get("FileSystemArn", fs_id)
                        for mt_page in efs_client.get_paginator("describe_mount_targets").paginate(FileSystemId=fs_id):
                            for mt in mt_page.get("MountTargets", []):
                                mt_id = mt["MountTargetId"]
                                subnet = mt.get("SubnetId")
                                vpc = mt.get("VpcId")
                                if subnet:
                                    rels.append(self.relationship(fs_arn, mt_id, self.HAS_MOUNT_TARGET, "EFSFileSystem", "EFSMountTarget"))
                                    rels.append(self.relationship(mt_id, subnet, self.IN_SUBNET, "EFSMountTarget", "Subnet"))
                                if vpc:
                                    rels.append(self.relationship(fs_arn, vpc, self.IN_VPC, "EFSFileSystem", "VPC"))
            except Exception:
                pass
            return rels
        return self.scan_regions("efs", collect)
